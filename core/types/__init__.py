"""
Core Types Module
공통 타입 정의 및 커스텀 예외
"""

from core.types.agent_types import (
    AgentResult,
    AgentType,
    SQLAgentState,
    HRAgentState,
)
from core.types.errors import (
    HRAgentError,
    SQLExecutionError,
    RAGRetrievalError,
    RouterError,
    DatabaseConnectionError,
)

__all__ = [
    # Types
    "AgentResult",
    "AgentType",
    "SQLAgentState",
    "HRAgentState",
    # Errors
    "HRAgentError",
    "SQLExecutionError",
    "RAGRetrievalError",
    "RouterError",
    "DatabaseConnectionError",
]
