from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.schemas import IResponse

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    result: str
    usage: Optional[dict] = None

@router.post("/chat", response_model=IResponse[ChatResponse])
async def chat_completion(request: ChatRequest):
    print(f"DEBUG: Received Chat Request: {request.model_dump()}")
    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY is not configured")
    
    try:
        client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
        )
        
        completion = client.chat.completions.create(
            model=settings.DEFAULT_LLM_MODEL,
            messages=[m.model_dump() for m in request.messages],
            temperature=request.temperature
        )
        
        content = completion.choices[0].message.content
        print(f"DEBUG: LLM Raw Output: {content}")
        
        data = ChatResponse(
            result=content,
            usage=completion.usage.model_dump() if completion.usage else None
        )
        
        return IResponse.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
