"""
HR Agent - 통합 HR Agent (LangGraph 기반)

사용법:
    agent = HRAgent(router=router, sql_agent=sql_agent, rag_agent=rag_agent)
    result = agent.query("직원 수는?")
"""

from typing import Literal

from langgraph.graph import StateGraph, END

from core.types.agent_types import HRAgentState, AgentResult
from core.routing.router import Router
from core.agents.sql_agent import SQLAgent
from core.agents.rag_agent import RAGAgent


class HRAgent:
    """
    HR 통합 Agent (LangGraph 기반)

    - 의존성 주입으로 Router, SQLAgent, RAGAgent 받음
    - Router로 질문 분류
    - SQL Agent 또는 RAG Agent로 처리
    """

    def __init__(
        self,
        router: Router,  # 의존성 주입
        sql_agent: SQLAgent,  # 의존성 주입
        rag_agent: RAGAgent,  # 의존성 주입
        verbose: bool = False,
    ):
        """
        Args:
            router: Router 인스턴스 (주입)
            sql_agent: SQLAgent 인스턴스 (주입)
            rag_agent: RAGAgent 인스턴스 (주입)
            verbose: 디버그 출력 여부
        """
        self.router = router
        self.sql_agent = sql_agent
        self.rag_agent = rag_agent
        self.verbose = verbose

        self.app = self._build_graph()

    def _log(self, message: str):
        """디버그 로그 출력"""
        if self.verbose:
            print(message)

    def _route_node(self, state: HRAgentState) -> HRAgentState:
        """질문을 분석하여 Agent 선택"""
        try:
            agent_type = self.router.route(state["question"])
            self._log(f"[Router] 질문: {state['question']}")
            self._log(f"[Router] 선택된 Agent: {agent_type}")
            return {**state, "agent_type": agent_type}
        except Exception as e:
            # 라우팅 실패 시 RAG로 폴백
            self._log(f"[Router] 오류, RAG로 폴백: {e}")
            return {**state, "agent_type": "RAG_AGENT", "error": str(e)}

    def _sql_agent_node(self, state: HRAgentState) -> HRAgentState:
        """SQL Agent 실행"""
        self._log("[SQL Agent] 질문 처리 중...")

        try:
            result = self.sql_agent.query(state["question"])
            self._log("[SQL Agent] 완료")
            return {**state, "agent_result": result, "error": ""}
        except Exception as e:
            self._log(f"[SQL Agent] 오류: {e}")
            error_result = AgentResult(
                success=False,
                answer=f"SQL Agent 오류: {str(e)}",
                metadata={"agent_type": "SQL_AGENT"},
                error=str(e),
            )
            return {**state, "agent_result": error_result, "error": str(e)}

    def _rag_agent_node(self, state: HRAgentState) -> HRAgentState:
        """RAG Agent 실행"""
        self._log("[RAG Agent] 질문 처리 중...")

        try:
            result = self.rag_agent.query(state["question"])
            self._log("[RAG Agent] 완료")
            return {**state, "agent_result": result, "error": ""}
        except Exception as e:
            self._log(f"[RAG Agent] 오류: {e}")
            error_result = AgentResult(
                success=False,
                answer=f"RAG Agent 오류: {str(e)}",
                metadata={"agent_type": "RAG_AGENT"},
                error=str(e),
            )
            return {**state, "agent_result": error_result, "error": str(e)}

    def _route_to_agent(self, state: HRAgentState) -> Literal["sql_agent", "rag_agent"]:
        """Agent 타입에 따라 다음 노드 결정"""
        if state["agent_type"] == "SQL_AGENT":
            return "sql_agent"
        else:
            return "rag_agent"

    def _build_graph(self) -> StateGraph:
        """LangGraph 구성"""
        workflow = StateGraph(HRAgentState)

        # 노드 추가
        workflow.add_node("router", self._route_node)
        workflow.add_node("sql_agent", self._sql_agent_node)
        workflow.add_node("rag_agent", self._rag_agent_node)

        # 엣지 추가
        workflow.set_entry_point("router")

        # 조건부 라우팅
        workflow.add_conditional_edges(
            "router",
            self._route_to_agent,
            {"sql_agent": "sql_agent", "rag_agent": "rag_agent"},
        )

        # Agent 실행 후 종료
        workflow.add_edge("sql_agent", END)
        workflow.add_edge("rag_agent", END)

        return workflow.compile()

    def query(self, question: str) -> AgentResult:
        """
        질문에 대한 답변 생성

        Args:
            question: 사용자 질문

        Returns:
            AgentResult: 통일된 결과 형식
        """
        # 빈 문자열 검증
        if not question or not question.strip():
            return AgentResult(
                success=False,
                answer="질문을 입력해주세요.",
                metadata={"agent_type": "VALIDATION"},
                error="Empty question",
            )

        initial_state: HRAgentState = {
            "question": question,
            "agent_type": "",
            "agent_result": None,
            "error": "",
        }

        result = self.app.invoke(initial_state)

        # 하위 Agent 결과 반환
        if result.get("agent_result"):
            return result["agent_result"]

        # 오류 시 폴백
        return AgentResult(
            success=False,
            answer=result.get("error", "Unknown error"),
            metadata={"agent_type": result.get("agent_type", "UNKNOWN")},
            error=result.get("error"),
        )

    def stream(self, question: str):
        """
        스트리밍 응답 (향후 구현)

        Args:
            question: 사용자 질문

        Yields:
            상태 업데이트
        """
        initial_state: HRAgentState = {
            "question": question,
            "agent_type": "",
            "agent_result": None,
            "error": "",
        }

        for state in self.app.stream(initial_state):
            yield state
