"""
Health Check Endpoint

헬스체크 API
"""

from fastapi import APIRouter
from app.models import HealthResponse
from app.core.config import settings

# 🔥 prefix 필수
router = APIRouter(prefix="/health")


@router.get(
    "",
    response_model=HealthResponse,
    summary="헬스체크",
    description="API 서버 상태 확인",
    response_description="서버 상태 및 버전"
)
async def health() -> HealthResponse:
    """
    헬스체크 엔드포인트
    
    서버가 정상적으로 작동하는지 확인합니다.
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION
    )