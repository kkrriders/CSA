from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


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
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Test Settings
    DEFAULT_QUESTION_TIME: int = 90  # seconds
    MIN_QUESTIONS: int = 5
    MAX_QUESTIONS: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
