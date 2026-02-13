"""
DashScope 文本嵌入服务
"""
from langchain_community.embeddings import DashScopeEmbeddings
from app.core.config import settings


def get_embedding_model():
    """
    获取 DashScope 嵌入模型实例
    
    Returns:
        DashScopeEmbeddings: 嵌入模型实例
    """
    if not settings.DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY is not configured")
    
    return DashScopeEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dashscope_api_key=settings.DASHSCOPE_API_KEY,
    )
