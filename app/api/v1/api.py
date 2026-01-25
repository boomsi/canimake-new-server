from fastapi import APIRouter
from app.api.v1.endpoints import llm, kitchen, meta

api_router = APIRouter()
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(kitchen.router, prefix="/kitchen", tags=["kitchen"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
