"""
Router - 질문 의도 분류기

사용법:
    router = Router(model="gpt-4o-mini")
    agent_type = router.route("직원 수는?")
    # agent_type = "SQL_AGENT" 또는 "RAG_AGENT"
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core.types.agent_types import AgentType
from core.types.errors import RouterError


class Router:
    """
    질문 의도 분류 Router

    - SQL_AGENT: 데이터베이스 조회
    - RAG_AGENT: 문서 검색
    """

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Args:
            model: OpenAI 모델명
            temperature: LLM temperature (0=결정적)
        """
        self.model = model
        self.temperature = temperature
        self._init_chain()

    def _init_chain(self):
        """분류 체인 초기화"""
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)

        # 프롬프트 (현업 스타일 - 경계 케이스 중심 Few-shot)
        template = """HR 시스템 질문 분류기입니다.

<핵심 기준>
- SQL_AGENT: 특정 데이터를 조회하려는 의도 (누가, 몇 명, 얼마, 몇 번, 목록)
- RAG_AGENT: 규정/제도/절차 자체를 묻는 의도 (어떤 규정, 어떻게 하는지)

<헷갈리기 쉬운 케이스>
"급여 알 수 있는 방법" → SQL_AGENT (급여 데이터 조회 의도)
"휴가 신청 방법은?" → RAG_AGENT (신청 절차를 묻는 것)
"김철수 휴가 몇 번?" → SQL_AGENT (횟수 = 데이터 조회)
"휴가는 며칠인가요?" → RAG_AGENT (규정상 휴가 일수)
"지각한 직원 목록" → SQL_AGENT (데이터 목록 조회)
"지각하면 어떻게 되나요?" → RAG_AGENT (징계 규정)
"내 연봉 알려줘" → SQL_AGENT (연봉 데이터)
"연봉 협상은 어떻게?" → RAG_AGENT (절차/제도)

<출력>
SQL_AGENT 또는 RAG_AGENT 중 하나만 출력. 설명 금지.

질문: {question}
분류:"""

        prompt = ChatPromptTemplate.from_template(template)

        # 체인 (LCEL)
        self.chain = prompt | llm | StrOutputParser()

    def route(self, question: str) -> AgentType:
        """
        질문을 분석하여 적절한 Agent로 라우팅

        Args:
            question: 사용자 질문

        Returns:
            "SQL_AGENT" 또는 "RAG_AGENT"
        """
        try:
            result = self.chain.invoke({"question": question})
            agent_type = result.strip()

            # 검증
            if agent_type not in ["SQL_AGENT", "RAG_AGENT"]:
                # 기본값: RAG_AGENT (안전한 선택)
                return "RAG_AGENT"

            return agent_type

        except Exception as e:
            # 오류 시 기본값
            raise RouterError(f"라우팅 오류: {e}")
