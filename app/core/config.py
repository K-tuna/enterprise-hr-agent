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

    # === SQL Agent 설정 ===
    SQL_AGENT_MAX_ATTEMPTS: int = 3

    # === RAG Agent 설정 ===
    RAG_TOP_K: int = 3
    RAG_EMBEDDING_MODEL: str = "text-embedding-3-small"
    RAG_INDEX_PATH: Optional[str] = None  # None이면 기본 경로 사용

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
