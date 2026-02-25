"""
RAG Agent - 회사 규정 검색 및 답변 생성

사용법:
    agent = RAGAgent(model="gpt-4o-mini")
    result = agent.query("연차는 몇일인가요?")
"""

import logging
import os
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from core.types.agent_types import AgentResult
from core.types.errors import RAGRetrievalError
from core.llm.factory import create_chat_model, create_embeddings

logger = logging.getLogger(__name__)


class RAGAgent:
    """
    RAG Agent 클래스

    - FAISS 또는 OpenSearch 기반 벡터 검색
    - LLM 답변 생성
    """

    def __init__(
        self,
        model: str = os.environ.get("OLLAMA_MODEL"),
        temperature: float = 0,
        top_k: int = 5,
        embedding_model: str = os.environ.get("OLLAMA_EMBEDDING_MODEL"),
        index_path: Optional[str] = None,
        provider: str = os.environ.get("LLM_PROVIDER", "openai"),
        base_url: Optional[str] = os.environ.get("OLLAMA_BASE_URL"),
        # OpenSearch 관련 파라미터
        retriever_type: str = "opensearch",
        embedding_provider: Optional[str] = None,
        opensearch_url: str = "http://localhost:9200",
        opensearch_index_name: str = "hr_documents",
        opensearch_pipeline_name: str = "hr-hybrid-pipeline",
        opensearch_bm25_weight: float = 0.6,
        opensearch_knn_weight: float = 0.4,
    ):
        """
        Args:
            model: LLM 모델명
            temperature: LLM temperature (0=결정적)
            top_k: 검색할 상위 k개 문서
            embedding_model: 임베딩 모델명
            index_path: FAISS 인덱스 경로 (None이면 기본 경로)
            provider: LLM Provider ("openai" 또는 "ollama")
            base_url: Ollama 서버 URL (ollama일 때만 사용)
            retriever_type: 검색 엔진 타입 ("faiss" | "opensearch")
            embedding_provider: 임베딩 provider (None이면 provider 사용, 하위 호환)
            opensearch_url: OpenSearch 서버 URL
            opensearch_index_name: OpenSearch 인덱스명
            opensearch_pipeline_name: OpenSearch Search Pipeline명
            opensearch_bm25_weight: BM25 가중치
            opensearch_knn_weight: kNN 가중치
        """
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.embedding_model = embedding_model
        self.provider = provider
        self.base_url = base_url
        self.retriever_type = retriever_type
        self.embedding_provider = embedding_provider
        self.opensearch_url = opensearch_url
        self.opensearch_index_name = opensearch_index_name
        self.opensearch_pipeline_name = opensearch_pipeline_name
        self.opensearch_bm25_weight = opensearch_bm25_weight
        self.opensearch_knn_weight = opensearch_knn_weight

        # FAISS 인덱스 경로 설정
        if index_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.index_path = project_root / "data" / "faiss_index"
        else:
            self.index_path = Path(index_path)

        self._init_components()

    def _init_components(self):
        """Retriever, LLM, RAG Chain 초기화"""
        # Embeddings (embedding_provider 우선, 없으면 provider)
        self.embeddings = create_embeddings(
            provider=self.embedding_provider or self.provider,
            model=self.embedding_model,
            base_url=self.base_url,
        )

        # Retriever 분기
        if self.retriever_type == "opensearch":
            self._init_opensearch_retriever()
        else:
            self._init_faiss_retriever()

        # LLM
        self.llm = create_chat_model(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            base_url=self.base_url,
        )

        # 프롬프트
        template = """당신은 회사 인사 규정 전문가입니다.
아래 회사 규정 내용을 참고하여 질문에 정확하고 간결하게 답변하세요.
규정에 없는 내용은 "규정에서 해당 내용을 찾을 수 없습니다"라고 답하세요.

<규정 내용>
{context}
</규정 내용>

질문: {question}

답변:"""

        self.prompt = ChatPromptTemplate.from_template(template)

        # RAG Chain (LCEL)
        self.rag_chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _init_faiss_retriever(self):
        """FAISS 기반 Retriever 초기화"""
        if not self.index_path.exists():
            raise RAGRetrievalError(
                f"FAISS index not found at {self.index_path}. "
                "Please run scripts/build_index.py first."
            )

        self.vectorstore = FAISS.load_local(
            str(self.index_path),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.top_k}
        )
        logger.info("FAISS retriever 초기화 완료 (index: %s)", self.index_path)

    def _init_opensearch_retriever(self):
        """OpenSearch Hybrid Search Retriever 초기화"""
        from core.retrieval.opensearch_client import OpenSearchHybridClient

        self.opensearch_client = OpenSearchHybridClient(
            opensearch_url=self.opensearch_url,
            index_name=self.opensearch_index_name,
            pipeline_name=self.opensearch_pipeline_name,
            embeddings=self.embeddings,
            bm25_weight=self.opensearch_bm25_weight,
            knn_weight=self.opensearch_knn_weight,
        )

        # 연결 확인
        if not self.opensearch_client.health_check():
            raise RAGRetrievalError(
                f"OpenSearch 연결 실패: {self.opensearch_url}. "
                "docker-compose up opensearch -d 를 실행하세요."
            )

        # 문서 수 확인
        doc_count = self.opensearch_client.get_document_count()
        if doc_count == 0:
            raise RAGRetrievalError(
                f"OpenSearch 인덱스 '{self.opensearch_index_name}'에 문서가 없습니다. "
                "python scripts/build_opensearch_index.py --rebuild 를 실행하세요."
            )

        self.retriever = self.opensearch_client.get_retriever(k=self.top_k)
        logger.info(
            "OpenSearch retriever 초기화 완료 (index: %s, docs: %d, BM25=%.0f%%, kNN=%.0f%%)",
            self.opensearch_index_name,
            doc_count,
            self.opensearch_bm25_weight * 100,
            self.opensearch_knn_weight * 100,
        )

    def _format_docs(self, docs) -> str:
        """검색된 문서를 문자열로 포맷팅"""
        return "\n\n".join(doc.page_content for doc in docs)

    def query(self, question: str) -> AgentResult:
        """
        질문에 대한 답변 생성

        Args:
            question: 사용자 질문

        Returns:
            AgentResult: 통일된 결과 형식
        """
        try:
            # 검색
            source_docs = self.retriever.invoke(question)

            # 답변 생성
            answer = self.rag_chain.invoke(question)

            return AgentResult(
                success=True,
                answer=answer,
                metadata={
                    "agent_type": "RAG_AGENT",
                    "retriever_type": self.retriever_type,
                    "source_docs": [doc.page_content[:200] for doc in source_docs],
                },
                error=None,
            )

        except Exception as e:
            return AgentResult(
                success=False,
                answer="",
                metadata={"agent_type": "RAG_AGENT", "source_docs": []},
                error=str(e),
            )

    def stream(self, question: str):
        """
        스트리밍 응답 생성

        Args:
            question: 사용자 질문

        Yields:
            답변 청크 (문자열)
        """
        for chunk in self.rag_chain.stream(question):
            yield chunk
