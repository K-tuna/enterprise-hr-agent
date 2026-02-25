"""
Application Configuration
모든 설정을 한 곳에서 관리
"""

from typing import Optional, List
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """통합 애플리케이션 설정"""

    # === API 설정 ===
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Enterprise HR Agent"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered HR Agent with SQL and RAG capabilities"
    DEBUG: bool = False

    # === CORS ===
    CORS_ORIGINS: List[str] = ["*"]

    # === OpenAI 설정 ===
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # === LLM 설정 (통합) ===
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0

    # === LLM Provider 선택 ===
    # "openai" 또는 "ollama" 중 선택
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")

    # === Ollama 설정 (LLM_PROVIDER=ollama일 때 사용) ===
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")
    OLLAMA_EMBEDDING_MODEL: str = Field(default="nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")

    # === SQL Agent 설정 ===
    SQL_AGENT_MAX_ATTEMPTS: int = 3

    # === RAG Agent 설정 ===
    RAG_TOP_K: int = 5
    RAG_EMBEDDING_MODEL: str = "text-embedding-3-small"
    RAG_INDEX_PATH: Optional[str] = None  # None이면 기본 경로 사용

    # === RAG Retriever 타입 ===
    RAG_RETRIEVER_TYPE: str = Field(default="opensearch", env="RAG_RETRIEVER_TYPE")  # "faiss" | "opensearch"

    # === RAG Embedding 설정 (LLM Provider와 분리) ===
    RAG_EMBEDDING_PROVIDER: str = Field(default="huggingface", env="RAG_EMBEDDING_PROVIDER")

    # === OpenSearch 설정 ===
    OPENSEARCH_URL: str = Field(default="http://localhost:9200", env="OPENSEARCH_URL")
    OPENSEARCH_INDEX_NAME: str = Field(default="hr_documents", env="OPENSEARCH_INDEX_NAME")
    OPENSEARCH_PIPELINE_NAME: str = Field(default="hr-hybrid-pipeline", env="OPENSEARCH_PIPELINE_NAME")
    OPENSEARCH_BM25_WEIGHT: float = Field(default=0.6, env="OPENSEARCH_BM25_WEIGHT")
    OPENSEARCH_KNN_WEIGHT: float = Field(default=0.4, env="OPENSEARCH_KNN_WEIGHT")

    # === Database 설정 ===
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DB_POOL_SIZE: int = 5
    DB_POOL_RECYCLE: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환 (캐시됨)"""
    return Settings()


# 하위 호환성을 위한 인스턴스 (기존 코드에서 settings 직접 import 하는 경우)
settings = get_settings()
