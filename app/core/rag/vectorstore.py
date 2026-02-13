"""
ChromaDB 向量数据库操作封装
"""
import os
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from app.core.rag.embeddings import get_embedding_model
from app.core.config import settings


_vectorstore_instance: Optional[Chroma] = None


def get_vectorstore(collection_name: Optional[str] = None) -> Chroma:
    """
    获取或创建 ChromaDB 向量存储实例（单例模式）
    
    Args:
        collection_name: 集合名称，默认使用配置中的名称
    
    Returns:
        Chroma: ChromaDB 向量存储实例
    """
    global _vectorstore_instance
    
    if _vectorstore_instance is None:
        # 确保目录存在
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        
        collection = collection_name or settings.RAG_COLLECTION_NAME
        embedding_function = get_embedding_model()
        
        _vectorstore_instance = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            collection_name=collection,
            embedding_function=embedding_function,
        )
    
    return _vectorstore_instance


def add_documents(documents: List[Document]) -> List[str]:
    """
    添加文档到向量数据库
    
    Args:
        documents: 文档列表
    
    Returns:
        List[str]: 添加的文档 ID 列表
    """
    vectorstore = get_vectorstore()
    return vectorstore.add_documents(documents)


def similarity_search(
    query: str,
    k: int = None,
    filter: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """
    相似度搜索
    
    Args:
        query: 查询文本
        k: 返回结果数量，默认使用配置值
        filter: 元数据过滤条件
    
    Returns:
        List[Document]: 相关文档列表
    """
    vectorstore = get_vectorstore()
    k = k or settings.RAG_TOP_K
    
    if filter:
        return vectorstore.similarity_search(query, k=k, filter=filter)
    else:
        return vectorstore.similarity_search(query, k=k)


def similarity_search_with_score(
    query: str,
    k: int = None,
    filter: Optional[Dict[str, Any]] = None
) -> List[tuple]:
    """
    相似度搜索（带分数）
    
    Args:
        query: 查询文本
        k: 返回结果数量，默认使用配置值
        filter: 元数据过滤条件
    
    Returns:
        List[tuple]: (Document, score) 元组列表
    """
    vectorstore = get_vectorstore()
    k = k or settings.RAG_TOP_K
    
    if filter:
        return vectorstore.similarity_search_with_score(query, k=k, filter=filter)
    else:
        return vectorstore.similarity_search_with_score(query, k=k)
