"""
API v1 Router

v1 엔드포인트 통합
"""

from fastapi import APIRouter
from app.api.v1.endpoints import query, health

# v1 라우터
api_router = APIRouter()

# 엔드포인트 등록
api_router.include_router(query.router, tags=["Query"])
api_router.include_router(health.router, tags=["Health"])

