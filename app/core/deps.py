"""
Dependency Injection
FastAPI 의존성 주입 (Container 기반)
"""

from core.container import get_container
from core.agents import HRAgent


def get_hr_agent() -> HRAgent:
    """
    HRAgent 의존성 주입

    Returns:
        HRAgent 인스턴스 (Container에서 관리)
    """
    return get_container().hr_agent
