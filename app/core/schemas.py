from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class IResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
    
    @classmethod
    def success(cls, data: T, message: str = "success"):
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, code: int = 500, message: str = "error", data: Any = None):
        return cls(code=code, message=message, data=data)
