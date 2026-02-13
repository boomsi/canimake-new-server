from fastapi import APIRouter
from app.api.v1.endpoints import llm, kitchen, meta, rag

api_router = APIRouter()
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(kitchen.router, prefix="/kitchen", tags=["kitchen"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
