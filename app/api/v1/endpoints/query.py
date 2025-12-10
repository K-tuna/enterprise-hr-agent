"""
Query Endpoint

질의 처리 API
"""

from fastapi import APIRouter, Depends, HTTPException
from app.models import QueryRequest, QueryResponse
from app.services.hr_service import HRService
from app.core.deps import get_hr_service

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="HR 질의 처리",
    description="자연어 질문을 받아 SQL Agent 또는 RAG Agent로 처리합니다.",
    response_description="처리 결과 및 답변"
)
async def query(
    request: QueryRequest,
    hr_service: HRService = Depends(get_hr_service)
) -> QueryResponse:
    """
    질의 처리 엔드포인트
    
    - **question**: 사용자 질문 (필수)
    
    ## 예시
    - "직원은 총 몇 명인가요?" → SQL Agent
    - "연차휴가는 몇일인가요?" → RAG Agent
    """
    try:
        result = hr_service.process_query(request.question)
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"질의 처리 중 오류 발생: {str(e)}"
        )

