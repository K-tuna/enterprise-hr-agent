"""
Request Models

API 요청 Pydantic 모델
"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """질의 요청 모델"""
    
    question: str = Field(
        ...,
        description="사용자 질문",
        min_length=1,
        max_length=500,
        example="직원은 총 몇 명인가요?"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "연차휴가는 몇일인가요?"
            }
        }




