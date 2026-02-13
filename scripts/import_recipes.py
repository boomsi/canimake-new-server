#!/usr/bin/env python3
"""
菜谱数据导入脚本（并发优化版）

用法:
    python scripts/import_recipes.py --input recipes.json
    python scripts/import_recipes.py --input recipes.json --collection custom_collection
    python scripts/import_recipes.py --input recipes.json --batch-size 200 --workers 5
"""
import json
import argparse
import sys
import time
import threading
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.documents import Document

# 写入锁，确保 ChromaDB 写入操作的线程安全
_write_lock = threading.Lock()

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.rag.vectorstore import get_vectorstore
from app.core.config import settings


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    加载 JSON/JSONL 数据文件
    支持格式：
        1. JSON 数组: [{}, {}, ...]
        2. JSONL 格式: {}\n{}\n... (每行一个 JSON 对象)
        3. 单个 JSON 对象: {}
    
    Args:
        file_path: JSON/JSONL 文件路径
    
    Returns:
        List[Dict]: 菜谱数据列表
    """
    recipes = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # 读取第一行判断格式
        first_line = f.readline().strip()
        f.seek(0)  # 重置文件指针
        
        # 检查是否是 JSONL 格式（每行一个 JSON 对象）
        if first_line.startswith('{') and not first_line.startswith('[{'):
            # JSONL 格式：逐行读取
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                try:
                    recipe = json.loads(line)
                    recipes.append(recipe)
                except json.JSONDecodeError as e:
                    print(f"⚠️  第 {line_num} 行 JSON 解析失败（跳过）: {e}")
                    continue
        else:
            # 标准 JSON 格式（数组或单个对象）
            try:
                data = json.load(f)
                if isinstance(data, list):
                    recipes = data
                elif isinstance(data, dict):
                    recipes = [data]
                else:
                    raise ValueError(f"不支持的 JSON 格式: {type(data)}")
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 解析失败: {e}")
    
    return recipes


def recipe_to_document(recipe: Dict[str, Any]) -> Document:
    """
    将菜谱数据转换为 LangChain Document
    
    Args:
        recipe: 菜谱字典
    
    Returns:
        Document: LangChain 文档对象
    """
    # 构建文档内容
    content_parts = []
    
    # 菜名
    if recipe.get('name'):
        content_parts.append(f"菜名：{recipe['name']}")
    
    # 标准菜名
    if recipe.get('dish') and recipe['dish'] != 'Unknown':
        content_parts.append(f"标准菜名：{recipe['dish']}")
    
    # 描述
    if recipe.get('description'):
        content_parts.append(f"描述：{recipe['description']}")
    
    # 食材
    if recipe.get('recipeIngredient'):
        ingredients = ', '.join(recipe['recipeIngredient'])
        content_parts.append(f"食材：{ingredients}")
    
    # 步骤
    if recipe.get('recipeInstructions'):
        steps_text = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(recipe['recipeInstructions'])])
        content_parts.append(f"步骤：\n{steps_text}")
    
    # 关键词
    if recipe.get('keywords'):
        keywords = ', '.join(recipe['keywords'])
        content_parts.append(f"关键词：{keywords}")
    
    content = '\n\n'.join(content_parts)
    
    # 构建元数据
    metadata = {
        "name": recipe.get('name', ''),
        "dish": recipe.get('dish', 'Unknown'),
        "author": recipe.get('author', ''),
    }
    
    return Document(page_content=content, metadata=metadata)


def import_batch(documents: List[Document], batch_num: int, total_batches: int) -> tuple:
    """
    导入一批文档（线程安全）
    
    Args:
        documents: 文档列表
        batch_num: 批次编号
        total_batches: 总批次数
    
    Returns:
        tuple: (成功数量, 失败数量, 错误信息)
    """
    try:
        vectorstore = get_vectorstore()
        # 使用锁确保写入操作的线程安全
        # 注意：LangChain 的 add_documents 内部会批量调用嵌入 API
        with _write_lock:
            doc_ids = vectorstore.add_documents(documents)
        return (len(doc_ids), 0, None)
    except ImportError as e:
        # 处理缺少依赖的情况
        error_msg = str(e)
        if 'dashscope' in error_msg.lower():
            return (0, len(documents), "缺少 dashscope 包，请运行: pip install dashscope")
        return (0, len(documents), f"导入错误: {error_msg}")
    except Exception as e:
        return (0, len(documents), str(e))


def import_recipes(
    json_file: str,
    collection_name: str = None,
    batch_size: int = 200,
    max_workers: int = 5
):
    """
    并发导入菜谱数据到向量数据库
    
    Args:
        json_file: JSON 文件路径
        collection_name: 集合名称（可选，默认使用配置值）
        batch_size: 每批处理的文档数量
        max_workers: 最大并发数
    """
    start_time = time.time()
    print(f"📖 开始导入菜谱数据：{json_file}")
    print(f"⚙️  配置：批次大小={batch_size}, 并发数={max_workers}")
    
    # 加载数据
    try:
        recipes = load_json_data(json_file)
        print(f"✅ 成功加载 {len(recipes)} 条菜谱数据")
    except Exception as e:
        print(f"❌ 加载 JSON 文件失败：{e}")
        return
    
    # 转换为文档
    print("🔄 转换文档格式...")
    documents = []
    failed_conversions = 0
    for recipe in recipes:
        try:
            doc = recipe_to_document(recipe)
            documents.append(doc)
        except Exception as e:
            failed_conversions += 1
            if failed_conversions <= 5:  # 只显示前5个错误
                print(f"⚠️  转换菜谱失败（跳过）：{e}")
            continue
    
    if failed_conversions > 5:
        print(f"⚠️  还有 {failed_conversions - 5} 个转换失败")
    
    if not documents:
        print("❌ 没有有效的文档可导入")
        return
    
    total_docs = len(documents)
    print(f"📝 准备导入 {total_docs} 个文档...")
    
    # 分批处理
    batches = []
    for i in range(0, total_docs, batch_size):
        batch = documents[i:i + batch_size]
        batches.append(batch)
    
    total_batches = len(batches)
    print(f"📦 分为 {total_batches} 批处理（每批 {batch_size} 条）")
    
    # 并发导入
    success_count = 0
    fail_count = 0
    completed_batches = 0
    
    print("\n🚀 开始并发导入...")
    print("=" * 60)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_batch = {
            executor.submit(import_batch, batch, i + 1, total_batches): i + 1
            for i, batch in enumerate(batches)
        }
        
        # 处理完成的任务
        for future in as_completed(future_to_batch):
            batch_num = future_to_batch[future]
            try:
                success, failed, error = future.result()
                success_count += success
                fail_count += failed
                completed_batches += 1
                
                # 显示进度
                progress = (completed_batches / total_batches) * 100
                print(f"[{completed_batches}/{total_batches}] 批次 {batch_num} 完成: "
                      f"✅ {success} 条成功, ❌ {failed} 条失败 "
                      f"(进度: {progress:.1f}%)")
                
                if error:
                    print(f"   错误: {error}")
            except Exception as e:
                fail_count += len(batches[batch_num - 1])
                completed_batches += 1
                print(f"[{completed_batches}/{total_batches}] 批次 {batch_num} 异常: {e}")
    
    # 统计结果
    elapsed_time = time.time() - start_time
    print("=" * 60)
    print(f"\n✅ 导入完成！")
    print(f"📊 统计信息：")
    print(f"   - 总文档数: {total_docs}")
    print(f"   - 成功导入: {success_count}")
    print(f"   - 失败数量: {fail_count}")
    print(f"   - 耗时: {elapsed_time:.2f} 秒 ({elapsed_time/60:.2f} 分钟)")
    if success_count > 0:
        print(f"   - 平均速度: {success_count/elapsed_time:.2f} 条/秒")
    print(f"📊 数据库路径：{settings.CHROMA_DB_PATH}")
    print(f"📚 集合名称：{collection_name or settings.RAG_COLLECTION_NAME}")


def main():
    parser = argparse.ArgumentParser(description="导入菜谱数据到 RAG 向量数据库（并发优化版）")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="输入的 JSON 文件路径"
    )
    parser.add_argument(
        "--collection",
        "-c",
        default=None,
        help="向量数据库集合名称（可选）"
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=200,
        help="每批处理的文档数量（默认: 200）"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=5,
        help="最大并发数（默认: 5，建议不超过 10 以避免 API 限流）"
    )
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not Path(args.input).exists():
        print(f"❌ 文件不存在：{args.input}")
        return
    
    # 检查配置
    if not settings.DASHSCOPE_API_KEY:
        print("⚠️  警告：DASHSCOPE_API_KEY 未配置，将无法生成向量")
        print("   请在 .env 文件中设置 DASHSCOPE_API_KEY")
        return
    
    # 参数验证
    if args.batch_size < 1:
        print("❌ 批次大小必须大于 0")
        return
    
    if args.workers < 1:
        print("❌ 并发数必须大于 0")
        return
    
    if args.workers > 20:
        print("⚠️  警告：并发数过大可能导致 API 限流，建议不超过 10")
    
    # 执行导入
    import_recipes(
        args.input,
        args.collection,
        batch_size=args.batch_size,
        max_workers=args.workers
    )


if __name__ == "__main__":
    main()
