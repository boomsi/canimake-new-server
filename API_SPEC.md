# CanIMake API 接口文档

本文档包含了当前项目的所有 API 路由，方便开发者或 AI 获取接口详情。

## 通用响应格式
所有接口均返回以下统一 JSON 格式：
```json
{
  "code": 200,      // 200 表示成功，其他表示错误码
  "message": "success",
  "data": { ... }   // 具体业务数据
}
```

---

## 1. 基础接口 (Root)

### 1.1 服务状态检核
- **地址**: `/`
- **方式**: `GET`
- **说明**: 检查 API 服务是否正在运行。
- **返回值示例**:
```json
{
  "message": "Welcome to CanIMake API",
  "status": "running"
}
```

---

## 2. 元数据接口 (Meta)
标签：`meta`

### 2.1 获取预设厨具列表
- **地址**: `/api/v1/meta/appliances`
- **方式**: `GET`
- **说明**: 获取系统预设的常用厨具列表。
- **示例参数**: 无
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": ["炒锅", "煎锅", "微波炉", "烤箱", "空气炸锅", "奶锅", "蒸屉"]
}
```

### 2.2 获取热门食材列表
- **地址**: `/api/v1/meta/ingredients/trending`
- **方式**: `GET`
- **说明**: 获取当前热门或推荐的食材列表。
- **示例参数**: 无
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": ["螺丝椒", "香葱", "鸡蛋", "西红柿", "土豆", "牛腩", "海白虾"]
}
```

---

## 3. 厨房核心接口 (Kitchen)
标签：`kitchen`

### 3.1 生成菜谱列表
- **地址**: `/api/v1/kitchen/recipes`
- **方式**: `POST`
- **说明**: 根据提供的食材和厨具，利用 AI 生成推荐菜谱。
- **请求参数示例**:
```json
{
  "ingredients": ["西红柿", "鸡蛋", "牛腩"],
  "appliances": ["炒锅", "电饭煲"]
}
```
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "recipes": [
      {
        "dish_name": "经典西红柿炖牛腩",
        "difficulty": "中等",
        "prep_time": "60分钟",
        "tags": ["家常菜", "高蛋白", "暖胃"],
        "nutrition": {
          "calories": "450kcal",
          "protein": "35g",
          "fat": "25g",
          "carbs": "10g"
        },
        "ingredients": {
          "main": ["牛腩 500g", "西红柿 3个"],
          "pantry_needed": ["油", "盐", "生姜", "料酒"]
        },
        "pre_prep": ["牛腩切块焯水", "西红柿去皮切块"],
        "steps": ["热锅凉油，下姜片爆香", "放入牛腩翻炒至变色", "加入西红柿块炒出汁", "加水没过食材，中小火炖煮50分钟"],
        "pro_tip": "西红柿一定要炒出油，颜色才漂亮。"
      }
    ]
  }
}
```

---

## 4. 语言模型接口 (LLM)
标签：`llm`

### 4.1 通用对话接口
- **地址**: `/api/v1/llm/chat`
- **方式**: `POST`
- **说明**: 直接与后台配置的 LLM 模型进行对话。
- **请求参数示例**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "简单的介绍一下如何煎牛排？"
    }
  ],
  "temperature": 0.7
}
```
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "result": "煎牛排的关键在于：1. 室温回温... 2. 擦干表面... 3. 大火热锅...",
    "usage": {
      "prompt_tokens": 20,
      "completion_tokens": 50,
      "total_tokens": 70
    }
  }
}
```

---

## 5. RAG 检索增强生成接口 (RAG)
标签：`rag`

### 5.1 RAG 知识库问答
- **地址**: `/api/v1/rag/chat`
- **方式**: `POST`
- **说明**: 基于向量数据库的检索增强生成（RAG）问答接口。与 `/llm/chat` 的区别是：
  - 会先从向量数据库中检索相关的菜谱知识
  - 将检索到的知识作为上下文提供给 LLM
  - 返回答案的同时提供知识来源信息
- **请求参数示例**:
```json
{
  "query": "如何做西红柿鸡蛋？",
  "top_k": 3
}
```
- **参数说明**:
  - `query` (必填): 用户问题
  - `top_k` (可选): 检索的文档数量，默认使用配置值（通常为 3）
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "西红柿鸡蛋是一道经典的家常菜。制作步骤：1. 将西红柿切块，鸡蛋打散...",
    "sources": [
      {
        "content": "菜名：西红柿炒鸡蛋\n标准菜名：西红柿炒鸡蛋\n描述：经典家常菜...",
        "name": "西红柿炒鸡蛋",
        "dish": "西红柿炒鸡蛋",
        "author": ""
      }
    ],
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 80,
      "total_tokens": 230
    }
  }
}
```
- **返回值说明**:
  - `answer`: LLM 基于检索到的知识生成的回答
  - `sources`: 检索到的相关菜谱来源列表，包含：
    - `content`: 菜谱内容片段（前 200 字符）
    - `name`: 菜谱名称
    - `dish`: 标准菜名
    - `author`: 作者（如果有）
  - `usage`: Token 使用量统计（如果可用）
- **注意事项**:
  - 如果向量数据库中没有相关数据，`sources` 将返回空数组，`answer` 会提示未找到相关信息
  - 需要先通过 `scripts/import_recipes.py` 导入菜谱数据到向量数据库

### 5.2 RAG 增强的菜谱生成
- **地址**: `/api/v1/rag/recipes`
- **方式**: `POST`
- **说明**: 基于向量数据库检索相似菜谱，然后生成符合用户食材和厨具的菜谱方案。与 `/kitchen/recipes` 的区别是：
  - 会先从向量数据库中检索相关的菜谱知识
  - 基于检索到的菜谱生成更贴合实际的菜谱方案
  - 返回格式与 `/kitchen/recipes` 完全一致
- **请求参数示例**:
```json
{
  "ingredients": ["西红柿", "鸡蛋", "牛腩"],
  "appliances": ["炒锅", "电饭煲"]
}
```
- **参数说明**:
  - `ingredients` (必填): 食材列表
  - `appliances` (可选): 厨具列表，默认为空
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "recipes": [
      {
        "dish_name": "经典西红柿炖牛腩",
        "difficulty": "中等",
        "prep_time": "60分钟",
        "tags": ["家常菜", "高蛋白", "暖胃"],
        "nutrition": {
          "calories": "450kcal",
          "protein": "35g",
          "fat": "25g",
          "carbs": "10g"
        },
        "ingredients": {
          "main": ["牛腩 500g", "西红柿 3个"],
          "pantry_needed": ["油 (少许)", "盐 (一勺)", "生姜 (3片)", "料酒 (1勺)"]
        },
        "pre_prep": ["牛腩切块焯水", "西红柿去皮切块"],
        "steps": [
          "热锅凉油，下姜片爆香",
          "放入牛腩翻炒至变色",
          "加入西红柿块炒出汁",
          "加水没过食材，中小火炖煮50分钟"
        ],
        "pro_tip": "西红柿一定要炒出油，颜色才漂亮。"
      }
    ]
  }
}
```
- **返回值说明**:
  - 返回格式与 `/api/v1/kitchen/recipes` 完全相同
  - `recipes`: 菜谱列表，每个菜谱包含完整的制作信息
- **注意事项**:
  - 如果向量数据库中没有相关数据，会返回空数组 `{"recipes": []}`
  - 需要先通过 `scripts/import_recipes.py` 导入菜谱数据到向量数据库
  - 相比 `/kitchen/recipes`，此接口生成的菜谱更贴合实际，因为参考了向量数据库中的真实菜谱

---

## 附录：数据导入

### 导入菜谱数据到向量数据库

在使用 RAG 接口之前，需要先将菜谱数据导入到向量数据库。

**命令格式**:
```bash
python scripts/import_recipes.py --input <json_file> [选项]
```

**参数说明**:
- `--input` / `-i` (必填): JSON 文件路径
- `--collection` / `-c` (可选): 向量数据库集合名称，默认使用配置值
- `--batch-size` / `-b` (可选): 每批处理的文档数量，默认 200
- `--workers` / `-w` (可选): 最大并发数，默认 5（建议不超过 10）

**使用示例**:
```bash
# 基本用法
python scripts/import_recipes.py --input recipes.json

# 指定集合名称
python scripts/import_recipes.py --input recipes.json --collection my_recipes

# 自定义批次大小和并发数
python scripts/import_recipes.py --input recipes.json --batch-size 100 --workers 3
```

**支持的 JSON 格式**:
- JSON 数组: `[{}, {}, ...]`
- JSONL 格式: 每行一个 JSON 对象
- 单个 JSON 对象: `{}`

**菜谱 JSON 结构示例**:
```json
{
  "name": "西红柿炒鸡蛋",
  "dish": "西红柿炒鸡蛋",
  "description": "经典家常菜",
  "recipeIngredient": ["西红柿", "鸡蛋", "油", "盐"],
  "recipeInstructions": ["将西红柿切块", "鸡蛋打散", "热锅下油", "炒制"],
  "keywords": ["家常菜", "简单"],
  "author": "张三"
}
```

**注意事项**:
- 需要配置 `DASHSCOPE_API_KEY` 环境变量（用于生成向量）
- 导入过程会调用 DashScope 嵌入模型 API，会产生费用
- 向量数据库文件存储在 `./data/chroma_db` 目录（可在配置中修改）
