from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import json
from openai import OpenAI
from app.core.config import settings
from app.core.prompts import KITCHEN_SYSTEM_PROMPT
from app.core.schemas import IResponse

router = APIRouter()

class KitchenRequest(BaseModel):
    ingredients: List[str]
    appliances: Optional[List[str]] = None

class Nutrition(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    calories: str
    protein: str
    fat: str
    carbs: str

class Ingredients(BaseModel):
    main: List[str]
    pantry_needed: List[str]

class Recipe(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    dish_name: str
    difficulty: str
    prep_time: str
    tags: List[str]
    nutrition: Nutrition
    ingredients: Ingredients
    pre_prep: List[str]
    steps: List[str]
    pro_tip: str

class KitchenResponse(BaseModel):
    recipes: List[Recipe]

from app.core.mock_data import MOCK_KITCHEN_RESPONSE

@router.post("/recipes", response_model=IResponse[KitchenResponse])
async def get_recipes(request: KitchenRequest):
    print(f"DEBUG: Received Kitchen Request: {request.model_dump()}")
    
    # Mock Mode
    if settings.MOCK_LLM:
        print("DEBUG: [MOCK MODE] Returning pre-defined recipe data.")
        data = KitchenResponse(**MOCK_KITCHEN_RESPONSE)
        return IResponse.success(data=data)

    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY is not configured")
    
    try:
        client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
        )
        
        ingredients_str = ", ".join(request.ingredients)
        appliances_str = ", ".join(request.appliances) if request.appliances else "常规厨具"
        
        completion = client.chat.completions.create(
            model=settings.DEFAULT_LLM_MODEL,
            messages=[
                {"role": "system", "content": KITCHEN_SYSTEM_PROMPT},
                {"role": "user", "content": f"我的食材有：{ingredients_str}。我可用的厨具有：{appliances_str}。"}
            ],
            response_format={"type": "json_object"}  # Ensure JSON output if supported by model/sdk
        )
        
        content = completion.choices[0].message.content
        print(f"LLM Raw Output: {content}")
        
        # Parse the JSON string from LLM to ensure it's valid before returning
        try:
            recipes_data = json.loads(content)
            data = KitchenResponse(**recipes_data)
            return IResponse.success(data=data)
        except Exception as e:
            print(f"Parsing/Validation Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"LLM output validation error: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
