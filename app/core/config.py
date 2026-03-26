from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://pip_user:pip_password@localhost:5432/payment_intelligence"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Ollama (local LLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # Embedding model (local, free)
    embedding_model: str = "all-MiniLM-L6-v2"

    # RAG settings
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k_results: int = 5

    # Cache
    cache_ttl: int = 3600  # 1 hour

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()