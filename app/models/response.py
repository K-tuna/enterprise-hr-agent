"""
Response Models

API 응답 Pydantic 모델
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    """질의 응답 모델"""
    
    question: str = Field(..., description="원본 질문")
    answer: str = Field(..., description="최종 답변")
    agent_type: str = Field(..., description="사용된 Agent 타입 (SQL_AGENT | RAG_AGENT)")
    success: bool = Field(..., description="성공 여부")
    error: Optional[str] = Field(None, description="오류 메시지 (실패 시)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "직원은 총 몇 명인가요?",
                "answer": "4",
                "agent_type": "SQL_AGENT",
                "success": True,
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    
    status: str = Field(..., description="서비스 상태")
    version: str = Field(..., description="API 버전")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }




