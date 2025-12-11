"""
Agent Types
모든 Agent의 통일된 타입 정의
"""

from typing import TypedDict, Dict, Any, Optional, List, Literal


# ===== Agent 타입 =====
AgentType = Literal["SQL_AGENT", "RAG_AGENT"]


# ===== 통일된 Agent 결과 =====
class AgentResult(TypedDict):
    """모든 Agent의 통일된 반환 타입"""
    success: bool
    answer: str
    metadata: Dict[str, Any]  # agent_type, sql, source_docs 등
    error: Optional[str]


# ===== SQL Agent State (LangGraph용) =====
class SQLAgentState(TypedDict):
    """SQL Agent의 LangGraph 상태"""
    question: str
    schema: str
    sql: str
    error: Optional[str]
    results: Optional[List[Dict[str, Any]]]
    attempt: int
    max_attempts: int


# ===== HR Agent State (LangGraph용) =====
class HRAgentState(TypedDict):
    """HR Agent의 LangGraph 상태"""
    question: str
    agent_type: str
    agent_result: Optional[AgentResult]
    error: str
