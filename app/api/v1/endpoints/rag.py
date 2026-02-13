"""
RAG 知识库查询端点
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from app.core.schemas import IResponse
from app.core.rag.chain import rag_query, rag_recipes
from app.api.v1.endpoints.kitchen import KitchenRequest, KitchenResponse

router = APIRouter()


class RAGChatRequest(BaseModel):
    """RAG 聊天请求模型"""
    query: str  # 用户问题
    top_k: Optional[int] = None  # 检索数量，默认使用配置值


class SourceInfo(BaseModel):
    """来源信息模型"""
    content: str
    name: Optional[str] = None
    dish: Optional[str] = None
    author: Optional[str] = None


class RAGChatResponse(BaseModel):
    """RAG 聊天响应模型"""
    answer: str  # LLM 生成的回答
    sources: List[SourceInfo]  # 引用的菜谱来源
    usage: Optional[Dict[str, Any]] = None  # Token 使用量


@router.post("/chat", response_model=IResponse[RAGChatResponse])
async def rag_chat(request: RAGChatRequest):
    """
    RAG 知识库问答接口
    
    基于向量检索和 LLM 生成回答，与 /llm/chat 的区别是加入了 RAG 检索增强
    """
    try:
        # 调用 RAG 查询
        result = rag_query(query=request.query, top_k=request.top_k)
        
        # 转换 sources 格式
        sources = [
            SourceInfo(**source) for source in result["sources"]
        ]
        
        data = RAGChatResponse(
            answer=result["answer"],
            sources=sources,
            usage=result["usage"],
        )
        
        return IResponse.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/recipes", response_model=IResponse[KitchenResponse])
async def rag_recipes_endpoint(request: KitchenRequest):
    """
    RAG 增强的菜谱生成接口
    
    基于向量数据库检索相似菜谱，然后生成符合用户食材和厨具的菜谱方案。
    与 /kitchen/recipes 的区别是：
    - 会先从向量数据库中检索相关的菜谱知识
    - 基于检索到的菜谱生成更贴合实际的菜谱方案
    - 返回格式与 /kitchen/recipes 完全一致
    """
    try:
        # 调用 RAG 菜谱生成
        result = rag_recipes(
            ingredients=request.ingredients,
            appliances=request.appliances or [],
            top_k=None  # 使用默认值
        )
        
        # 解析 JSON 字符串
        try:
            recipes_data = json.loads(result["recipes"])
            data = KitchenResponse(**recipes_data)
            return IResponse.success(data=data)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM output JSON parsing error: {str(e)}\nRaw output: {result['recipes'][:500]}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Response validation error: {str(e)}\nRaw output: {result['recipes'][:500]}"
            )
            
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG recipes generation failed: {str(e)}")
