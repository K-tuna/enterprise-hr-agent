"""
HR Service

비즈니스 로직 레이어
"""

from typing import Dict, Any
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.graph import HRAgent
from app.core.config import settings


class HRService:
    """HR 비즈니스 로직 서비스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.agent = HRAgent(
            model=settings.DEFAULT_MODEL,
            verbose=False
        )
    
    def process_query(self, question: str) -> Dict[str, Any]:
        """
        질문 처리
        
        Args:
            question: 사용자 질문
            
        Returns:
            처리 결과
        """
        result = self.agent.query(question)
        
        # 응답 포맷팅
        return {
            "question": result["question"],
            "answer": result["final_answer"],
            "agent_type": result["agent_type"],
            "success": result["success"],
            "error": result.get("error")
        }

