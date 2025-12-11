"""
FastAPI Main Application
현업 표준 구조 + DI Container
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.api import api_router
from core.container import init_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 수명주기 관리

    Startup:
    - DI Container 초기화
    - DB 연결 테스트

    Shutdown:
    - 정리 작업
    """
    # Startup
    settings = get_settings()
    container = init_container(settings)

    # DB 연결 테스트 (DATABASE_URL이 설정된 경우에만)
    if settings.DATABASE_URL:
        try:
            container.db.test_connection()
            print("✅ DB 연결 성공!")
        except Exception as e:
            print(f"⚠️ DB 연결 실패 (나중에 연결 시도): {e}")

    yield

    # Shutdown
    print("👋 애플리케이션 종료")


settings = get_settings()

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# 루트 엔드포인트
@app.get("/", tags=["Root"])
async def root():
    """
    루트 엔드포인트

    API 정보 제공
    """
    return {
        "message": "Enterprise HR Agent API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
