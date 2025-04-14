from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "pass123"
    POSTGRES_DB: str = "alrounder"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_USER: str = "elastic"  # Default Elasticsearch username
    ELASTICSEARCH_PASSWORD: str = ""  # Default is empty for local development
    SELENIUM_REMOTE_URL:str= "http://localhost:4444/wd/hub"
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES", mode="before")
    def validate_expire_minutes(cls, v):
        if isinstance(v, str):
            return int(v.strip().split()[0])  # Will strip off comments or spaces
        return v
    OPENAI_API_KEY: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings() 