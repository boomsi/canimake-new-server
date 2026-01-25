from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CanIMake API"
    DASHSCOPE_API_KEY: Optional[str] = None
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DEFAULT_LLM_MODEL: str = "qwen-plus"
    MOCK_LLM: bool = True
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
