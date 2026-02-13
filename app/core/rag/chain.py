"""
RAG 检索增强生成链
"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.core.rag.vectorstore import similarity_search
from app.core.config import settings


RAG_SYSTEM_PROMPT = """你是一个专业的菜谱助手。请根据以下菜谱信息回答用户问题。

参考菜谱：
{context}

要求：
1. 基于参考菜谱回答，不要编造
2. 如果参考信息不足，如实告知
3. 回答要实用、清晰
4. 可以适当总结和提炼关键信息
"""

RAG_RECIPES_SYSTEM_PROMPT = """
### 🤖 灵感厨房 (Inspiration Kitchen) - RAG 增强版

**Role**: 你是一位精通中式家常菜、现代营养学且极具生活智慧利用 AI 厨师长。你擅长利用用户冰箱里残余的少量食材，通过精妙的组合，为独自生活的年轻人创造出极简、健康且富有仪式感的美味。

**Task**: 根据用户输入的食材（及分量）以及可用的厨具，参考以下相似菜谱，设计 1-3 个最合理的烹饪方案。

**参考菜谱（必须基于这些菜谱生成，不要编造）**：
{context}

**Rules & Constraints**:
1. **必须基于参考菜谱**: **[极重要]** 你生成的菜谱必须基于以上参考菜谱，不能编造不存在的菜谱。可以根据用户的食材和厨具对参考菜谱进行调整、简化或组合，但核心做法必须来自参考菜谱。
2. **食材选取**: 必须以用户提供的食材为核心，但**不强制全部用到**。你可以根据风味和营养合理性选择其中的一部分进行组合。如果用户食材极少，请推荐最经典的搭配。
3. **食用安全**: **[极重要]** 必须充分考虑食材之间的相互影响，严禁推荐已知存在安全风险、搭配禁忌（如导致中毒、严重肠胃不适或破坏核心营养）的组合。
4. **厨具匹配**: 必须根据用户提供的"可用厨具列表"来设计方案。如果用户没有某种厨具（如：没有空气炸锅），则绝对不能推荐需要该厨具的菜谱。
5. **默认调味品**: 你可以默认用户拥有基础调料（油、盐、生抽、糖、醋）。如果需要其他特殊调料（如：蚝油、料酒、豆瓣酱），请在菜谱中注明为"建议添加"。
6. **调料分量化**: **[重要]** 在列出调料（pantry_needed）时，必须带上具体的分量或描述（如："食盐 一勺"、"生抽 2勺"、"白糖 适量"、"食用油 少许"）。
7. **厨具友好**: 优先利用用户现有的厨具。
8. **量化感知**: 如果某种食材分量极少（如：一根辣椒），请将其识别为"调味/配色用"；如果分量充足，则作为"主料"。
9. **预处理环节**: 必须包含食材的预处理指导（如：切块大小、是否泡水、去腥方法等），确保即使用户是新手也能从零开始处理。
10. **营养分析**: 必须提供每份菜品的近似热量（kcal）及三大营养素（蛋白质、脂肪、碳水）估算。
11. **语言风格**: 简洁、专业、充满鼓励，像是一位耐心的学长/学姐在教做饭。

**Output Format (Strict JSON)**:
你必须仅返回一个合法的 JSON 对象，不要包含任何额外的解释文字。格式如下：

{{
  "recipes": [
    {{
      "dish_name": "菜名",
      "tags": ["低卡", "高蛋白", "5分钟快手"],
      "nutrition": {{
        "calories": "数字+单位，如: 120kcal",
        "protein": "数字+单位，如: 12g",
        "fat": "数字+单位，如: 5g",
        "carbs": "数字+单位，如: 20g"
      }},
      "ingredients": {{
        "main": ["食材A (分量)", "食材B (分量)"],
        "pantry_needed": ["油 (少许)", "盐 (一勺)", "生抽 (2勺)"]
      }},
      "pre_prep": [
        "针对食材A的切法记录（如：逆着纹理切片）",
        "针对食材B的预处理（如：冷水浸泡15分钟去血水）"
      ],
      "steps": [
        "第一步烹饪描述...",
        "第二步烹饪描述..."
      ],
      "pro_tip": "一个能显著提升味道的小技巧"
    }}
  ]
}}
"""


def format_documents(docs: List[Document]) -> str:
    """
    格式化文档为上下文字符串
    
    Args:
        docs: 文档列表
    
    Returns:
        str: 格式化后的上下文
    """
    formatted = []
    for i, doc in enumerate(docs, 1):
        content = doc.page_content
        metadata = doc.metadata
        
        # 构建文档信息
        doc_info = f"【菜谱 {i}】"
        if "name" in metadata:
            doc_info += f"\n菜名：{metadata['name']}"
        if "dish" in metadata:
            doc_info += f"\n标准菜名：{metadata['dish']}"
        
        doc_info += f"\n内容：\n{content}\n"
        formatted.append(doc_info)
    
    return "\n---\n".join(formatted)


def get_rag_chain():
    """
    获取 RAG 链（返回 LLM 实例，用于后续调用）
    
    Returns:
        ChatOpenAI: LLM 实例
    """
    if not settings.DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY is not configured")
    
    return ChatOpenAI(
        model=settings.DEFAULT_LLM_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL,
        temperature=0.7,
    )


def rag_query(
    query: str,
    top_k: int = None,
    filter: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    执行 RAG 查询
    
    Args:
        query: 用户问题
        top_k: 检索数量
        filter: 元数据过滤条件
    
    Returns:
        Dict: 包含 answer, sources, usage 的字典
    """
    # 1. 向量检索
    docs = similarity_search(query, k=top_k or settings.RAG_TOP_K, filter=filter)
    
    if not docs:
        return {
            "answer": "抱歉，知识库中没有找到相关信息。",
            "sources": [],
            "usage": None,
        }
    
    # 2. 格式化上下文
    context = format_documents(docs)
    
    # 3. 构建提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM_PROMPT),
        ("human", "{question}"),
    ])
    
    # 4. 调用 LLM
    llm = get_rag_chain()
    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "question": query,
    })
    
    # 5. 提取来源信息
    sources = []
    for doc in docs:
        source_info = {
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
        }
        if doc.metadata:
            source_info.update({
                "name": doc.metadata.get("name", ""),
                "dish": doc.metadata.get("dish", ""),
                "author": doc.metadata.get("author", ""),
            })
        sources.append(source_info)
    
    # 6. 提取使用量信息（如果可用）
    usage = None
    if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
        usage = response.response_metadata["token_usage"]
    
    return {
        "answer": response.content,
        "sources": sources,
        "usage": usage,
    }


def rag_recipes(
    ingredients: List[str],
    appliances: List[str] = None,
    top_k: int = None
) -> Dict[str, Any]:
    """
    基于 RAG 检索结果，使用 LLM 生成菜谱
    
    Args:
        ingredients: 食材列表
        appliances: 厨具列表（可选）
        top_k: 检索数量
    
    Returns:
        Dict: 包含 recipes（JSON字符串）、sources、usage 的字典
    """
    import json
    
    # 1. 构建查询字符串
    ingredients_str = ", ".join(ingredients)
    query = f"食材：{ingredients_str}"
    if appliances:
        query += f"，厨具：{', '.join(appliances)}"
    
    # 2. 向量检索
    docs = similarity_search(query, k=top_k or settings.RAG_TOP_K)
    
    if not docs:
        # 如果没有检索到相关菜谱，返回空结果
        return {
            "recipes": json.dumps({"recipes": []}),
            "sources": [],
            "usage": None,
        }
    
    # 3. 格式化上下文（将检索到的菜谱作为上下文）
    context = format_documents(docs)
    
    # 4. 构建用户提示
    appliances_str = ", ".join(appliances) if appliances else "常规厨具"
    user_prompt = f"我的食材有：{ingredients_str}。我可用的厨具有：{appliances_str}。"
    
    # 5. 构建提示词（将上下文放入 system prompt）
    prompt = ChatPromptTemplate.from_messages([
        ("system", RAG_RECIPES_SYSTEM_PROMPT),
        ("human", "{question}"),
    ])
    
    # 6. 调用 LLM 生成菜谱
    llm = get_rag_chain()
    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "question": user_prompt,
    })
    
    # 7. 提取来源信息
    sources = []
    for doc in docs:
        source_info = {
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
        }
        if doc.metadata:
            source_info.update({
                "name": doc.metadata.get("name", ""),
                "dish": doc.metadata.get("dish", ""),
                "author": doc.metadata.get("author", ""),
            })
        sources.append(source_info)
    
    # 8. 提取使用量信息（如果可用）
    usage = None
    if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
        usage = response.response_metadata["token_usage"]
    
    # 9. 构建返回结果
    result = {
        "recipes": response.content,  # LLM 生成的 JSON 字符串
        "sources": sources,
        "usage": usage,
    }
    
    return result
