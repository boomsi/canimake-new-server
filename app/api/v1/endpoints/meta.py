from fastapi import APIRouter
from typing import List
from app.core.schemas import IResponse
from app.core.mock_data import PRESET_APPLIANCES, TRENDING_INGREDIENTS

router = APIRouter()

@router.get("/appliances", response_model=IResponse[List[str]])
async def get_preset_appliances():
    """获取预设厨具列表"""
    return IResponse.success(data=PRESET_APPLIANCES)

@router.get("/ingredients/trending", response_model=IResponse[List[str]])
async def get_trending_ingredients():
    """获取热门食材列表"""
    return IResponse.success(data=TRENDING_INGREDIENTS)
