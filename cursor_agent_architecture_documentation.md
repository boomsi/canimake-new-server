
**User**

好，现在这个项目只是基础的调用大模型相关的api调用对吧，现在我有计划增加对做饭相关的知识偏好，以让大模型回答更专业更精准的菜谱，营养推荐等信息，你有什么好的方案吗？先不修改，先说方案

---

**Cursor**

基于当前架构，我为你提供几个从简单到复杂的增强方案：

## 方案一：RAG（检索增强生成）+ 向量数据库 【推荐】

**核心思路**：构建烹饪知识库，根据用户输入的食材检索相关知识，注入到 LLM 的上下文中。

**技术栈**：
- 向量数据库：`Milvus` / `Qdrant` / `Chroma`（轻量级）
- 向量模型：`text-embedding-v3`（通义千问）或 `sentence-transformers`
- 知识库内容：食材属性、营养成分、烹饪技巧、搭配禁忌、时令特性

**架构变化**：
```
app/core/
├── knowledge/          # 新增
│   ├── embeddings.py  # 向量化服务
│   ├── retriever.py   # 知识检索
│   └── knowledge_base.json  # 知识库数据
```

**优点**：
- 可灵活扩展知识库
- 成本低，响应快
- 可追溯知识来源

**缺点**：
- 需要准备高质量知识库数据
- 需要部署向量数据库

---

## 方案二：Prompt 工程增强 + Few-shot 学习 【最快实现】

**核心思路**：优化现有 Prompt，加入大量优质示例和详细规则。

**改进点**：
1. 扩充 `prompts.py`，增加：
   - 100+ 常见食材的详细属性（营养、禁忌、最佳烹饪方式）
   - 10-20 个高质量菜谱示例（Few-shot）
   - 营养计算公式和参考标准
   
2. 动态 Prompt 组装：根据用户输入的食材，从知识库中提取相关段落动态插入

**架构变化**：
```
app/core/
├── prompts.py         # 优化现有
├── knowledge_data.py  # 新增：结构化知识数据
└── prompt_builder.py  # 新增：动态组装 Prompt
```

**优点**：
- 实现最快，无需额外依赖
- 不需要部署额外服务
- 对现有架构改动最小

**缺点**：
- Prompt 长度受限（Token 限制）
- 知识更新需要重启服务
- 无法处理大规模知识库

---

## 方案三：知识图谱 + 规则引擎 【最专业】

**核心思路**：构建食材-营养-烹饪方法的知识图谱，通过图数据库查询最优组合。

**技术栈**：
- 图数据库：`Neo4j` 或纯 Python 图结构
- 规则引擎：定义食材搭配规则、营养计算规则
- LLM 作为"语言生成器"，而非"知识源"

**架构变化**：
```
app/
├── knowledge/
│   ├── graph_db.py    # 图数据库操作
│   ├── rules.py       # 搭配规则引擎
│   └── nutrition.py   # 营养计算模块
└── services/          # 新增服务层
    └── recipe_generator.py  # 菜谱生成逻辑
```

**工作流程**：
1. 用户输入食材 → 图数据库查询食材属性和关系
2. 规则引擎筛选合理搭配 + 计算营养
3. 将结构化数据交给 LLM 生成自然语言描述

**优点**：
- 最专业、最精准
- 可解释性强（基于规则，而非"黑盒"）
- 知识复用率高

**缺点**：
- 开发成本高
- 需要人工梳理知识图谱
- 系统复杂度增加

---

## 方案四：混合方案（RAG + 知识增强 Prompt）【平衡方案】

**核心思路**：结合方案一和方案二的优点。

**实现步骤**：
1. 用轻量级向量数据库（如 Chroma）存储核心知识
2. 根据用户输入检索 Top-K 相关知识
3. 将检索结果 + Few-shot 示例动态组装到 Prompt
4. 送入 LLM 生成菜谱

**架构变化**：
```
app/
├── core/
│   ├── knowledge_data.py   # 结构化知识
│   ├── prompt_builder.py   # 动态 Prompt
│   └── retriever.py        # 向量检索
└── storage/
    └── chroma_db/          # 本地向量库
```

**优点**：
- 平衡了灵活性和复杂度
- 知识库可增量更新
- 成本可控

**缺点**：
- 需要学习向量数据库的使用
- 初期需要准备知识数据

---

## 我的建议

**如果你想快速验证效果**：先用 **方案二**（Prompt 增强），1-2 天内可以上线。

**如果你追求长期可扩展**：用 **方案四**（混合方案），投入 1 周开发，后续维护成本低。

**如果你想做到极致专业**：用 **方案三**（知识图谱），但需要投入 2-4 周，适合作为产品核心竞争力。

你倾向于哪个方案？或者我可以根据你的具体需求（开发周期、预算、知识库规模）进一步细化方案。

---

**User**

1. 如何构建烹饪知识库？这些知识从哪里获取呢？知识库数据如何获取？
2. 方案二就相当于直接在 prompt 内置一些烹饪的数据对吗？
3. 方案三的 图知识库数据从哪里来？
这几个方案分别都需要什么关键的数据？或者技术？或者第三方服务？

---

**Cursor**

很好的问题！让我详细解答每个方案的数据来源和技术依赖：

## 一、烹饪知识库数据来源（通用）

### 1. 开源数据集
- **中华菜谱数据集**：GitHub 上有开源项目
  - `chinese-recipe-dataset`（约 5 万条菜谱）
  - `chinese-food-knowledge-graph`（食材关系图谱）
- **国家食物成分表**：中国疾病预防控制中心营养与健康所发布
- **维基百科**：爬取食材、营养、烹饪技法相关词条

### 2. 公开 API
- **营养数据 API**：
  - USDA FoodData Central（美国农业部，免费）
  - 薄荷健康 API（中文，付费）
- **菜谱 API**：
  - 下厨房（需爬虫，注意合规）
  - 豆果美食（需爬虫）

### 3. LLM 生成（冷启动方案）
- 用通义千问批量生成结构化知识：
  ```
  提示词："请提供西红柿的详细信息：营养成分、适合搭配的食材、禁忌、最佳烹饪方式"
  ```
- 生成后人工审核和补充

### 4. 人工编写（高质量）
- 邀请营养师/厨师编写核心知识
- 从书籍整理：《中国居民膳食指南》、《食物成分表》

---

## 二、方案对比：数据需求和技术依赖

### 方案一：RAG + 向量数据库

**需要的数据**：
```json
[
  {
    "id": "ingredient_001",
    "name": "西红柿",
    "category": "蔬菜",
    "nutrition": {
      "calories_per_100g": 19,
      "protein": 0.9,
      "fat": 0.2,
      "carbs": 4.0,
      "vitamin_c": 19
    },
    "best_match": ["鸡蛋", "牛肉", "豆腐"],
    "avoid": ["黄瓜（破坏维生素C）"],
    "cooking_tips": "高温快炒锁住营养，炒出汁更香",
    "season": ["夏季"],
    "description": "西红柿富含番茄红素，加热后更易吸收..."
  }
]
```

**技术依赖**：
- 向量数据库：`Chroma`（最轻量，本地文件存储，无需额外服务）
  ```bash
  pip install chromadb
  ```
- 向量模型：
  - 通义千问 `text-embedding-v3` API（付费，0.0007元/千tokens）
  - 或开源模型 `m3e-base`（免费，本地运行）
    ```bash
    pip install sentence-transformers
    ```

**数据量估算**：
- 100 种常见食材
- 50 条烹饪技巧
- 30 条营养原则
- 总计约 **5000-10000 tokens**

**获取方式**：
1. 从开源数据集提取（GitHub: `chinese-food-knowledge-graph`）
2. 用 LLM 批量生成并人工审核
3. 逐步积累用户反馈优化

---

### 方案二：Prompt 工程增强

**是的，就是直接在 Prompt 中内置数据！**

**需要的数据示例**：
```python
KITCHEN_KNOWLEDGE = """
### 食材知识库
- 西红柿：19kcal/100g，富含维生素C和番茄红素。最佳搭配：鸡蛋、牛肉。禁忌：黄瓜同食破坏VC。
- 鸡蛋：147kcal/100g，优质蛋白。烹饪：冷水下锅煮8分钟即可。
- 牛腩：125kcal/100g，高蛋白。需焯水去血水，炖煮1小时以上。

### 营养计算参考
- 成年人每日推荐：1800-2400kcal，蛋白质 60-75g
- 减脂人群：控制在 1200-1500kcal

### Few-shot 示例
用户输入：["西红柿", "鸡蛋"]，厨具：["炒锅"]
输出：{
  "dish_name": "番茄炒蛋",
  "nutrition": {"calories": "180kcal", "protein": "12g"}
  ...
}
"""
```

**技术依赖**：
- **无额外依赖**，只需优化现有 `prompts.py`

**数据量限制**：
- 通义千问 `qwen-plus` 上下文限制：128k tokens
- 建议 Prompt 总长度控制在 **8000-10000 tokens**（约 100 种食材的核心信息）

**获取方式**：
1. 手动整理 100 种常见食材的核心信息（1-2 天）
2. 从《中国食物成分表》提取营养数据
3. 编写 10-20 个高质量菜谱示例

**优缺点**：
- ✅ 最快实现，无需额外服务
- ✅ 知识直接可见，易于调试
- ❌ 知识量受 Token 限制
- ❌ 更新需要重新部署

---

### 方案三：知识图谱

**需要的数据结构**：
```python
# 节点
Ingredient(name, category, nutrition)
CookingMethod(name, temperature, time)
Dish(name, cuisine_type)

# 关系
(西红柿)-[:MATCHES]->(鸡蛋)  # 搭配关系
(西红柿)-[:AVOID]->(黄瓜)    # 禁忌关系
(西红柿)-[:COOKED_BY]->(炒)  # 烹饪方式
(番茄炒蛋)-[:USES]->(西红柿) # 菜品使用
(番茄炒蛋)-[:REQUIRES]->(炒锅) # 所需厨具
```

**技术依赖**：
- **轻量级方案**：用 `networkx` 纯 Python 实现
  ```bash
  pip install networkx
  ```
  无需数据库，直接内存图结构

- **重量级方案**：`Neo4j` 图数据库
  ```bash
  # Docker 运行
  docker run -p 7474:7474 -p 7687:7687 neo4j
  pip install neo4j
  ```

**数据量估算**：
- 200 种食材节点
- 100 种烹饪方法节点
- 500+ 关系边
- 总计约 **1000 个节点 + 2000 条关系**

**数据来源**：
1. **GitHub 开源知识图谱**：
   - `chinese-food-knowledge-graph`（已有部分食材关系）
   - 需要人工扩充和验证
2. **爬取菜谱网站** 自动提取关系（需注意合规）
3. **LLM 辅助生成**：
   ```
   提示词："请列出西红柿可以搭配的所有食材，以及不能搭配的食材"
   ```

---

### 方案四：混合方案（RAG + Prompt）

**数据需求** = 方案一 + 方案二的数据
- 向量库：详细知识（同方案一）
- Prompt：核心规则 + Few-shot 示例（同方案二）

**技术依赖**：
- Chroma 向量库
- 向量模型（通义或 m3e）
- 无额外服务

---

## 三、实际可行的数据获取路径（推荐）

### 快速启动方案（1-3天）

1. **用 LLM 批量生成基础知识库**
   ```python
   # 脚本示例
   ingredients = ["西红柿", "鸡蛋", "土豆", ...]
   for ing in ingredients:
       prompt = f"请提供{ing}的营养成分、最佳搭配、禁忌、烹饪技巧"
       knowledge = call_llm(prompt)
       save_to_json(knowledge)
   ```

2. **从国家食物成分表补充营养数据**
   - 下载 Excel：http://www.chinanutri.cn
   - 转为 JSON 格式

3. **人工审核和优化**
   - 重点审核禁忌搭配（涉及安全）
   - 补充特色烹饪技巧

### 长期优化方案

1. **用户反馈循环**
   - 收集用户生成的菜谱反馈
   - 不断优化知识库

2. **专家标注**
   - 邀请营养师审核营养数据
   - 邀请厨师补充烹饪技巧

---

## 四、我的具体建议

**第一阶段（1周）**：方案二 + LLM 生成数据
- 用通义千问生成 100 种常见食材的结构化知识
- 直接内置到 Prompt 中
- **成本**：约 100 元（API 调用费用）
- **技术门槛**：低

**第二阶段（2-3周）**：升级到方案四
- 将 Prompt 中的知识迁移到 Chroma 向量库
- 实现动态检索
- **成本**：免费（用开源向量模型）
- **技术门槛**：中

**第三阶段（长期）**：引入知识图谱（可选）
- 如果需要复杂的食材关系推理
- 比如："用户缺少某种食材，推荐可替代的食材"

---

你想先从哪个阶段开始？如果选方案二，我可以帮你：
1. 写一个脚本批量生成知识库数据
2. 设计结构化的知识格式
3. 优化现有 Prompt

---

**User**

你好像没有推荐方案一？更推荐方案四？

---

**Cursor**

你观察得很仔细！让我解释一下我的推荐逻辑：

## 为什么没有单独推荐方案一？

**方案一（纯 RAG）的问题**：
- RAG 需要向量检索，检索质量依赖**大量高质量数据**
- 如果知识库数据不足（比如只有 100 条），检索效果不如直接写在 Prompt 里
- **冷启动困难**：初期数据少，检索召回率低，用户体验差

**方案四（RAG + Prompt）的优势**：
- 结合了两者优点：
  - **Prompt 部分**：放核心规则、Few-shot 示例（保底质量）
  - **RAG 部分**：放详细知识、边缘 case（提升上限）
- 即使检索失败，Prompt 中的核心知识也能保证基本回答质量

---

## 方案对比：一 vs 四

| 维度 | 方案一（纯 RAG） | 方案四（RAG + Prompt） |
|------|-----------------|----------------------|
| **知识组织** | 全部在向量库 | 核心在 Prompt，详细在向量库 |
| **冷启动** | ❌ 需要大量数据才有效 | ✅ Prompt 保底，逐步积累向量库 |
| **响应速度** | 较慢（每次检索） | 快（高频知识直接命中 Prompt） |
| **知识更新** | ✅ 灵活，实时更新 | Prompt 需重启，向量库可更新 |
| **成本** | 向量化 + 检索成本 | Prompt 免费，检索按需 |
| **适用场景** | 知识库成熟后（>1000 条） | 从零启动，逐步演进 |

---

## 我更推荐方案四的原因

### 1. **渐进式演进路径**
```
阶段一：纯 Prompt（100 条核心知识）
    ↓ 数据积累
阶段二：Prompt + RAG（Prompt 100 条核心 + 向量库 500 条详细）
    ↓ 继续扩展
阶段三：完全 RAG（向量库 5000+ 条，Prompt 只保留规则）
```

### 2. **双保险机制**
```python
# 方案四的查询流程
def generate_recipe(ingredients):
    # 1. 先检索向量库（可能失败或召回不准）
    retrieved_knowledge = vector_search(ingredients)  
    
    # 2. 组装 Prompt（即使检索为空，也有核心知识保底）
    prompt = f"""
    {BASE_KNOWLEDGE}  # 核心规则，100% 可用
    
    检索到的相关知识：
    {retrieved_knowledge if retrieved_knowledge else "无"}
    
    用户食材：{ingredients}
    请生成菜谱...
    """
    
    return call_llm(prompt)
```

### 3. **成本优化**
- **高频知识** → Prompt（一次性 Token 成本）
- **低频知识** → 向量库（按需检索，节省 Prompt Token）

示例：
- "鸡蛋怎么煮" → 高频，放 Prompt
- "松露如何处理" → 低频，放向量库

---

## 但是！如果你满足以下条件，可以直接用方案一

✅ **已有现成的知识库数据**（比如爬到了 1000+ 条菜谱）  
✅ **愿意投入时间清洗和向量化数据**  
✅ **追求知识动态更新**（不想重启服务）

那么**方案一完全可行**！

---

## 具体建议

### 如果你现在没有现成数据 → **方案四**
```
Week 1: 用 LLM 生成 100 条核心知识 → 内置 Prompt
Week 2: 部署 Chroma 向量库，迁移数据
Week 3: 实现混合检索逻辑
```

### 如果你已有大量数据（或打算采购） → **方案一**
```
Week 1: 数据清洗 + 向量化
Week 2: 部署向量库 + 检索逻辑
Week 3: 调优检索策略（Top-K、相似度阈值）
```

---

## 那你现在的情况是？

1. **有现成的菜谱/食材数据吗？** 数量大概多少？
2. **开发周期要求**：希望多久上线第一版？
3. **预算**：愿意为 API 调用/数据采购投入多少？

根据你的回答，我可以给出更精准的方案选择！

或者我可以帮你：
- **快速验证方案二**（2 小时内实现，看效果是否满足需求）
- **搭建方案四的 MVP**（1 周完成最小可用版本）

你倾向于哪个？

---

**User**

方案四都需要什么？

---

**Cursor**

让我详细列出**方案四（RAG + Prompt 混合）**的完整需求清单：

## 一、技术依赖

### 1. Python 库
```bash
# 向量数据库（本地轻量级，无需额外服务）
pip install chromadb

# 向量模型（二选一）
# 选项A：用通义千问的 Embedding API（推荐，质量高）
pip install dashscope  

# 选项B：用开源模型（免费，本地运行）
pip install sentence-transformers
```

**现有依赖无需改动**：FastAPI、OpenAI SDK 等都继续用

### 2. 向量模型选择

| 方案 | 优点 | 缺点 | 成本 |
|------|------|------|------|
| **通义 text-embedding-v3** | 中文效果好，维护简单 | 需要 API 调用 | 0.0007元/千tokens（约100元可处理100万字） |
| **开源 m3e-base** | 完全免费，离线可用 | 需要本地下载模型（约400MB） | 0 元 |

**推荐**：先用**通义 Embedding**，成本很低（初期 10 元够用），后期数据量大再换开源

---

## 二、数据需求

### 1. 核心知识库数据（放 Prompt）
**约 100 条高频知识**，JSON 格式：

```json
{
  "core_ingredients": [
    {
      "name": "西红柿",
      "nutrition_per_100g": "19kcal, 蛋白质0.9g, 脂肪0.2g, 碳水4g",
      "best_match": ["鸡蛋", "牛肉", "豆腐"],
      "avoid": ["黄瓜（破坏维生素C）"],
      "cooking_tip": "高温快炒，炒出汁"
    }
  ],
  "cooking_rules": [
    "焯水去腥：牛肉、羊肉等需冷水下锅焯水",
    "营养搭配：主食+蛋白质+蔬菜"
  ],
  "few_shot_examples": [
    {
      "input": ["西红柿", "鸡蛋"],
      "output": "番茄炒蛋菜谱..."
    }
  ]
}
```

**数据量**：约 **5000-8000 tokens**（占 Prompt 的 5-10%）

### 2. 详细知识库数据（放向量库）
**约 500-1000 条详细知识**，纯文本格式：

```text
西红柿的营养价值：
西红柿富含番茄红素，每100克含维生素C 19mg，具有抗氧化作用。
加热后番茄红素更易被人体吸收，建议炒制食用。
最佳搭配：鸡蛋（维生素D促进番茄红素吸收）、牛肉（蛋白质互补）。
禁忌搭配：黄瓜同食会破坏维生素C。
烹饪技巧：先炒西红柿出汁再炒蛋，颜色更红亮。
适合厨具：炒锅、不粘锅。
```

**数据量**：每条 200-500 字，总计约 **10-50 万字**

---

## 三、代码结构变化



```
app/
├── main.py
├── api/v1/
│   ├── api.py
│   └── endpoints/
│       ├── kitchen.py       # [修改] 集成检索逻辑
│       ├── llm.py
│       └── meta.py
├── core/
│   ├── config.py            # [修改] 新增向量库配置
│   ├── schemas.py
│   ├── prompts.py           # [修改] 优化为动态 Prompt
│   ├── mock_data.py
│   ├── knowledge_data.py    # [新增] 核心知识数据
│   └── prompt_builder.py    # [新增] 动态组装 Prompt
├── knowledge/               # [新增] 知识库模块
│   ├── __init__.py
│   ├── embeddings.py        # 向量化服务
│   ├── retriever.py         # 检索逻辑
│   └── data/                # 知识数据目录
│       ├── core.json        # 核心知识（给 Prompt 用）
│       └── detailed.txt     # 详细知识（给向量库用）
└── storage/                 # [新增] 本地存储
    └── chroma_db/           # Chroma 向量库文件
```

**需要新增的文件**：约 5 个核心文件

---

## 四、具体实现步骤

### Step 1: 准备数据（1-2 天）

#### 方式A：用 LLM 批量生成（推荐）
```python
# scripts/generate_knowledge.py
from openai import OpenAI

ingredients = ["西红柿", "鸡蛋", "土豆", "牛肉", ...]  # 100 种常见食材

for ingredient in ingredients:
    prompt = f"""
    请提供{ingredient}的详细信息，包括：
    1. 营养成分（每100g）
    2. 最佳搭配食材（3-5个）
    3. 禁忌搭配（如有）
    4. 烹饪技巧（2-3条）
    5. 适合的烹饪方式和厨具
    """
    
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 保存到文件
    save_knowledge(ingredient, response.choices[0].message.content)
```

**成本估算**：100 种食材 × 1000 tokens ≈ **20-30 元**

#### 方式B：从开源数据集获取（需要清洗）
- GitHub 搜索：`chinese recipe dataset`
- 下载 → 清洗 → 转为标准格式

### Step 2: 部署向量库（半天）

```python
# app/knowledge/embeddings.py
import chromadb
from chromadb.config import Settings

# 初始化本地向量库
client = chromadb.PersistentClient(
    path="./storage/chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name="cooking_knowledge",
    metadata={"description": "烹饪知识库"}
)

# 导入数据
def import_knowledge(texts: list[str]):
    collection.add(
        documents=texts,
        ids=[f"doc_{i}" for i in range(len(texts))]
    )
```

### Step 3: 实现检索逻辑（半天）

```python
# app/knowledge/retriever.py
from chromadb import Collection

def retrieve_knowledge(query: str, top_k: int = 3) -> list[str]:
    """根据查询检索相关知识"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results['documents'][0]

# 使用示例
# query = "西红柿和鸡蛋怎么搭配"
# knowledge = retrieve_knowledge(query)
# → ["西红柿富含番茄红素...", "鸡蛋含优质蛋白...", ...]
```

### Step 4: 动态 Prompt 组装（半天）

```python
# app/core/prompt_builder.py
from app.knowledge.retriever import retrieve_knowledge
from app.core.knowledge_data import CORE_KNOWLEDGE

def build_prompt(ingredients: list[str], appliances: list[str]) -> str:
    # 1. 加载核心知识（固定部分）
    base = CORE_KNOWLEDGE
    
    # 2. 检索相关详细知识（动态部分）
    query = f"食材：{', '.join(ingredients)}"
    retrieved = retrieve_knowledge(query, top_k=3)
    
    # 3. 组装完整 Prompt
    return f"""
{base}

### 检索到的相关知识：
{chr(10).join(retrieved)}

### 用户输入
食材：{ingredients}
厨具：{appliances}

请根据以上知识生成菜谱...
"""
```

### Step 5: 集成到接口（1 小时）

```python
# app/api/v1/endpoints/kitchen.py (修改)
from app.core.prompt_builder import build_prompt

@router.post("/recipes")
async def get_recipes(request: KitchenRequest):
    # 动态构建 Prompt
    prompt = build_prompt(
        ingredients=request.ingredients,
        appliances=request.appliances or []
    )
    
    # 调用 LLM
    client = OpenAI(...)
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"请生成菜谱"}
        ]
    )
    
    # 解析返回
    ...
```

---

## 五、成本估算

### 1. 开发成本
- **数据准备**：1-2 天（用 LLM 生成 + 人工审核）
- **代码实现**：2-3 天
- **测试优化**：1-2 天
- **总计**：约 **1 周**

### 2. 资金成本

| 项目 | 选项 | 费用 |
|------|------|------|
| **数据生成** | 通义千问 API | 20-50 元（一次性） |
| **向量化** | 通义 Embedding API | 10-30 元（一次性） |
| **向量化** | 开源模型 m3e | 0 元 |
| **向量库** | Chroma 本地 | 0 元 |
| **日常运行** | 检索 + LLM 调用 | 每千次请求约 5-10 元 |

**总预算**：
- **最低成本**：0 元（全用开源）
- **推荐配置**：100 元以内（用通义 API，质量更好）

### 3. 硬件要求
- **内存**：2GB 可用（如果用开源模型需要 4GB）
- **存储**：1GB（向量库数据 + 模型文件）
- **无需 GPU**

---

## 六、关键文件示例

### 1. 配置文件更新
```python
# app/core/config.py (新增配置)
class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # 向量库配置
    CHROMA_DB_PATH: str = "./storage/chroma_db"
    EMBEDDING_MODEL: str = "text-embedding-v3"  # 或 "m3e-base"
    RETRIEVAL_TOP_K: int = 3
```

### 2. 核心知识数据
```python
# app/core/knowledge_data.py
CORE_KNOWLEDGE = """
### 核心食材（高频 TOP 20）
西红柿：19kcal/100g，搭配鸡蛋/牛肉，禁忌黄瓜
鸡蛋：147kcal/100g，优质蛋白，冷水煮8分钟
...

### 烹饪规则
1. 肉类焯水：冷水下锅，去血水去腥
2. 营养搭配：主食+蛋白质+蔬菜

### Few-shot 示例
【示例1】
输入：["西红柿", "鸡蛋"], 厨具：["炒锅"]
输出：{菜谱 JSON}
"""
```

---

## 七、与现有架构的兼容性

**✅ 完全兼容**，只需：
1. 新增 `knowledge/` 模块
2. 修改 `kitchen.py` 集成检索
3. 其他接口（`/llm/chat`、`/meta/*`）**无需改动**

**✅ 可渐进式升级**：
- 先实现 Prompt 增强（不用向量库）
- 后续再加入向量检索

---

## 总结：方案四需要什么？

### 必需项 ✅
1. **Chroma 向量库**（pip install，无需额外服务）
2. **向量模型**（通义 API 或开源模型）
3. **100 条核心知识**（放 Prompt）
4. **500-1000 条详细知识**（放向量库）
5. **5 个新文件**（embeddings.py, retriever.py 等）

### 可选项 ⭕
- 开源数据集（如果自己生成数据可不用）
- GPU 加速（开源模型可选）

### 不需要 ❌
- 额外服务器（向量库本地运行）
- 数据库（Chroma 自己管理存储）
- 复杂配置（开箱即用）

---

**下一步**：你想让我帮你：
1. **写一个数据生成脚本**（用 LLM 批量生成知识）
2. **直接开始实现方案四**（我来写代码）
3. **先做一个简化的 Demo**（2 小时验证可行性）

你想从哪个开始？

