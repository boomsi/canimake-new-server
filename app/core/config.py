from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CanIMake API"
    DASHSCOPE_API_KEY: Optional[str] = None
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DEFAULT_LLM_MODEL: str = "qwen-plus"
    MOCK_LLM: bool = True
    DEBUG: bool = False
    
    # RAG 配置
    EMBEDDING_MODEL: str = "text-embedding-v4"  # 使用最新版本，兼容官方示例
    CHROMA_DB_PATH: str = "./data/chroma_db"
    RAG_TOP_K: int = 3
    RAG_COLLECTION_NAME: str = "recipes"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
