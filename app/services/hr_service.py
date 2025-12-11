"""
HR Service (Deprecated)

이 파일은 하위 호환성을 위해 유지됩니다.
새 코드에서는 core.container의 get_container().hr_agent를 사용하세요.
"""

from typing import Dict, Any

from core.container import get_container


class HRService:
    """
    HR 비즈니스 로직 서비스 (Deprecated)

    새 코드에서는 get_container().hr_agent를 직접 사용하세요.
    """

    def __init__(self):
        """서비스 초기화"""
        self._hr_agent = None

    @property
    def agent(self):
        """Lazy initialization"""
        if self._hr_agent is None:
            self._hr_agent = get_container().hr_agent
        return self._hr_agent

    def process_query(self, question: str) -> Dict[str, Any]:
        """
        질문 처리

        Args:
            question: 사용자 질문

        Returns:
            처리 결과
        """
        result = self.agent.query(question)

        return {
            "question": question,
            "answer": result["answer"],
            "agent_type": result["metadata"]["agent_type"],
            "success": result["success"],
            "error": result.get("error"),
        }
