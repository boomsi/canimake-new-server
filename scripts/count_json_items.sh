#!/bin/bash
# 统计 JSON/JSONL 文件中的项数
# 支持格式：
#   1. JSON 数组: [{}, {}, ...]
#   2. JSONL 格式: {}\n{}\n... (每行一个 JSON 对象)

if [ $# -eq 0 ]; then
    echo "用法: $0 <json_file>"
    echo "示例: $0 recipes.json"
    exit 1
fi

JSON_FILE="$1"

if [ ! -f "$JSON_FILE" ]; then
    echo "❌ 文件不存在: $JSON_FILE"
    exit 1
fi

# 使用 Python 统计（支持 JSON 数组和 JSONL 格式）
COUNT=$(python3 -c "
import json
import sys

try:
    with open('$JSON_FILE', 'r', encoding='utf-8') as f:
        # 尝试读取第一行
        first_line = f.readline().strip()
        f.seek(0)  # 重置文件指针
        
        # 检查是否是 JSONL 格式（每行一个 JSON 对象）
        if first_line.startswith('{') and not first_line.startswith('[{'):
            # JSONL 格式：每行一个 JSON 对象
            count = 0
            for line in f:
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        json.loads(line)
                        count += 1
                    except json.JSONDecodeError:
                        pass  # 跳过无效的 JSON 行
            print(count)
        else:
            # 标准 JSON 格式（数组或单个对象）
            data = json.load(f)
            if isinstance(data, list):
                print(len(data))
            elif isinstance(data, dict):
                print(1)
            else:
                print(0)
except Exception as e:
    print(f'错误: {e}', file=sys.stderr)
    sys.exit(1)
")

if [ $? -eq 0 ]; then
    echo "📊 文件: $JSON_FILE"
    echo "📝 项数: $COUNT"
else
    echo "❌ 统计失败"
    exit 1
fi
