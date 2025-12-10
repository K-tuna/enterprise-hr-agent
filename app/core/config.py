"""
Application Configuration

환경변수 및 설정 관리
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Enterprise HR Agent"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered HR Agent with SQL and RAG capabilities"
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # 프로덕션에서는 제한 필요
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # LLM 설정
    DEFAULT_MODEL: str = "gpt-4o-mini"
    DEFAULT_TEMPERATURE: float = 0.0
    
    class Config:
        case_sensitive = True


# 싱글톤 인스턴스
settings = Settings()

