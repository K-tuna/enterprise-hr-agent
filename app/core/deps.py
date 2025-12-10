"""
Dependency Injection

FastAPI 의존성 주입
"""

from typing import Generator
from app.services.hr_service import HRService


def get_hr_service() -> Generator[HRService, None, None]:
    """
    HRService 인스턴스 제공
    
    Yields:
        HRService 인스턴스
    """
    service = HRService()
    try:
        yield service
    finally:
        # 정리 작업 (필요시)
        pass

