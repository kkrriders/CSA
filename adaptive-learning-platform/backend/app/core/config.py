from pydantic_settings import BaseSettings
from typing import List, Union
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/adaptive_learning"
    MONGODB_DB_NAME: str = "adaptive_learning"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # ollama, huggingface, lmstudio, openrouter
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.1"
    LM_STUDIO_BASE_URL: str = "http://localhost:1234"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "mistralai/mistral-7b-instruct"

    # Application
    MAX_FILE_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "./uploads"
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:5173"

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutes default TTL

    # Email Configuration (optional)
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@adaptivelearning.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # Testing flag
    TESTING: bool = False

    # Test Settings
    DEFAULT_QUESTION_TIME: int = 90  # seconds
    MIN_QUESTIONS: int = 5
    MAX_QUESTIONS: int = 100

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
