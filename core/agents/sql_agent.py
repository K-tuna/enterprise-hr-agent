"""
SQL Agent (Refactored)
자연어 질문 → SQL 생성 → 실행 → Self-Correction

사용법:
    db = DatabaseConnection(connection_url="...")
    agent = SQLAgent(db=db, model="gpt-4o-mini")
    result = agent.query("직원 수는?")
"""

import re
from typing import Optional, List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from core.database.connection import DatabaseConnection
from core.types.agent_types import SQLAgentState, AgentResult


class SQLAgent:
    """
    SQL Agent (의존성 주입 적용)

    - 자연어 → SQL 생성
    - 실행 및 Self-Correction (최대 N회)
    - LangGraph 기반 워크플로우
    """

    def __init__(
        self,
        db: DatabaseConnection,  # 의존성 주입
        model: str = "gpt-4o-mini",
        max_attempts: int = 3,
    ):
        """
        Args:
            db: DatabaseConnection 인스턴스 (주입)
            model: OpenAI 모델명
            max_attempts: Self-Correction 최대 시도 횟수
        """
        self.db = db
        self.model = model
        self.max_attempts = max_attempts
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.app = self._build_workflow()

    def query(self, question: str) -> AgentResult:
        """
        질문에 대한 답변 생성

        Args:
            question: 사용자 질문

        Returns:
            AgentResult: 통일된 결과 형식
        """
        # 매 요청마다 최신 스키마 로딩
        schema = self.db.get_table_schema()

        state: SQLAgentState = {
            "question": question,
            "schema": schema,
            "sql": "",
            "error": None,
            "results": None,
            "attempt": 0,
            "max_attempts": self.max_attempts,
        }

        final = self.app.invoke(state)

        # 통일된 AgentResult 형식으로 변환
        success = final["error"] is None and final["results"] is not None

        if success:
            answer = self._generate_answer(question, final["results"])
        else:
            answer = f"SQL 실행 오류: {final['error']}"

        return AgentResult(
            success=success,
            answer=answer,
            metadata={
                "agent_type": "SQL_AGENT",
                "sql": final["sql"],
                "results": final["results"],
                "attempts": final["attempt"],
            },
            error=final["error"],
        )

    def _generate_answer(self, question: str, results: List[Dict[str, Any]]) -> str:
        """LLM으로 자연어 답변 생성"""
        if not results:
            return "조회 결과가 없습니다."

        prompt = ChatPromptTemplate.from_messages([
            ("system", "SQL 조회 결과를 바탕으로 질문에 자연스러운 한국어로 답변하세요. 간결하게 핵심만 답하세요."),
            ("user", "질문: {question}\n\nSQL 결과: {results}\n\n답변:")
        ])

        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"question": question, "results": str(results)})

    # --------------------------
    # Node: SQL Generation
    # --------------------------
    def _generate_sql_node(self, state: SQLAgentState) -> SQLAgentState:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 MySQL Text-to-SQL 전문가입니다.

⚠️ 절대 규칙:
1. 스키마에 존재하는 컬럼/테이블만 사용할 것
2. SELECT 쿼리만 생성 (UPDATE/DELETE 금지)
3. 설명/문장/마크다운/백틱 금지
4. 반드시 SQL로만 응답 (세미콜론으로 종료)
5. 새로운 컬럼명을 창조하지 말 것 (salary, annual_salary 금지)
6. 부서명 조회 시 departments.name 을 사용
7. employees.dept_id ↔ departments.dept_id 관계 사용
8. 평균 → AVG(), 수 → COUNT(), 부서별 → GROUP BY
""",
                ),
                (
                    "user",
                    """
=== SCHEMA START ===
{schema}
=== SCHEMA END ===

사용자 질문:
{question}

SQL만 출력하세요.
""",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        raw_sql = chain.invoke(
            {"schema": state["schema"], "question": state["question"]}
        ).strip()

        sql = self._clean_sql(raw_sql)

        return {**state, "sql": sql, "attempt": state["attempt"] + 1}

    # --------------------------
    # SQL Cleaner
    # --------------------------
    def _clean_sql(self, text: str) -> str:
        """LLM 출력에서 SQL만 안전하게 추출"""
        # 백틱 제거
        text = re.sub(r"```sql|```", "", text, flags=re.I).strip()

        # SELECT 위치부터만 SQL 인정
        lower = text.lower()
        idx = lower.find("select")
        if idx != -1:
            text = text[idx:].strip()

        # 세미콜론 자동 보정
        if not text.endswith(";"):
            text += ";"

        return text

    # --------------------------
    # Node: SQL Execution
    # --------------------------
    def _execute_sql_node(self, state: SQLAgentState) -> SQLAgentState:
        results, error = self.db.execute_query(state["sql"])

        if error:
            return {**state, "error": error, "results": None}
        return {**state, "error": None, "results": results}

    # --------------------------
    # Node: SQL Correction
    # --------------------------
    def _correction_node(self, state: SQLAgentState) -> SQLAgentState:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 SQL 오류 수정 전문가입니다.

규칙:
- SELECT 문만 출력
- 설명/문장 금지
- 스키마에 있는 컬럼만 사용
- 세미콜론으로 끝날 것
""",
                ),
                (
                    "user",
                    """
=== SCHEMA START ===
{schema}
=== SCHEMA END ===

원본 질문:
{question}

실패한 SQL:
{sql}

MySQL 오류:
{error}

수정된 SQL만 출력하세요.
""",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        corrected = chain.invoke(
            {
                "schema": state["schema"],
                "question": state["question"],
                "sql": state["sql"],
                "error": state["error"],
            }
        ).strip()

        corrected = self._clean_sql(corrected)

        return {**state, "sql": corrected, "error": None, "attempt": state["attempt"] + 1}

    # --------------------------
    # Conditional Edge
    # --------------------------
    def _should_retry(self, state: SQLAgentState) -> str:
        if state["error"] is None and state["results"] is not None:
            return "end"
        if state["attempt"] < state["max_attempts"]:
            return "correction"
        return "end"

    # --------------------------
    # Build LangGraph Workflow
    # --------------------------
    def _build_workflow(self):
        workflow = StateGraph(SQLAgentState)

        workflow.add_node("generate_sql", self._generate_sql_node)
        workflow.add_node("execute_sql", self._execute_sql_node)
        workflow.add_node("correction", self._correction_node)

        workflow.set_entry_point("generate_sql")
        workflow.add_edge("generate_sql", "execute_sql")

        workflow.add_conditional_edges(
            "execute_sql",
            self._should_retry,
            {"correction": "correction", "end": END},
        )

        workflow.add_edge("correction", "execute_sql")

        return workflow.compile()

    # --------------------------
    # Result Formatting
    # --------------------------
    def _format_results(self, results: Optional[List[Dict[str, Any]]]) -> str:
        """SQL 결과를 보기 좋게 포맷팅"""
        if not results:
            return "조회 결과가 없습니다."

        def format_value(v, key=""):
            """값 포맷팅 헬퍼"""
            if v is None:
                return None
            try:
                num = float(v)
                key_lower = key.lower()
                salary_keywords = ["salary", "base_salary", "급여", "연봉", "평균급여"]
                is_salary = any(kw in key_lower for kw in salary_keywords) or num >= 100000
                count_keywords = ["count", "직원수", "인원", "명", "employee"]
                is_count = any(kw in key_lower for kw in count_keywords)

                if is_salary and num >= 1000:
                    return f"{num:,.0f}원"
                elif is_count and num == int(num):
                    return f"{int(num)}명"
                elif num >= 1000:
                    return f"{num:,.0f}"
                elif num == int(num):
                    return str(int(num))
                return str(v)
            except (ValueError, TypeError):
                return str(v)

        # 단일 값인 경우
        if len(results) == 1 and len(results[0]) == 1:
            key = list(results[0].keys())[0]
            value = list(results[0].values())[0]
            formatted = format_value(value, key)
            if formatted is None:
                return "조회 결과가 없습니다."
            return formatted

        # 테이블 형태로 포맷팅
        output = []
        for row in results[:10]:  # 최대 10개만 표시
            row_dict = dict(row)
            formatted_parts = []
            for k, v in row_dict.items():
                formatted = format_value(v, k)
                if formatted is None:
                    continue
                formatted_parts.append(f"{k}: {formatted}")
            output.append(" | ".join(formatted_parts))

        if len(results) > 10:
            output.append(f"... 외 {len(results) - 10}개 행")

        return "\n".join(output)
