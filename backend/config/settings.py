import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisFlow"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # PostgreSQL Database URL (defaults to local SQLite if Postgres is unavailable)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aegisflow")
    
    # IBM watsonx.ai & IBM Granite (loaded via environment variables)
    WATSONX_API_KEY: Optional[str] = os.getenv("WATSONX_API_KEY", None)
    WATSONX_PROJECT_ID: Optional[str] = os.getenv("WATSONX_PROJECT_ID", None)
    WATSONX_URL: str = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    MODEL_ID: Optional[str] = os.getenv("MODEL_ID", "ibm/granite-4-h-small")
    WATSONX_RAG_COLLECTION_ID: Optional[str] = os.getenv("WATSONX_RAG_COLLECTION_ID", "supply_chain_contracts_v1")
    DATA_PREP_KIT_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
