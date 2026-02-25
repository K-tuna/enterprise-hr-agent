"""
DI Container
의존성 주입 컨테이너

사용법:
    from core.container import init_container, get_container

    # 초기화 (앱 시작 시)
    container = init_container()

    # 사용
    hr_agent = get_container().hr_agent
"""

from dataclasses import dataclass, field
from typing import Optional
from functools import cached_property

from app.core.config import Settings, get_settings
from core.database.connection import DatabaseConnection
from core.routing.router import Router
from core.agents.sql_agent import SQLAgent
from core.agents.rag_agent import RAGAgent
from core.agents.hr_agent import HRAgent


@dataclass
class Container:
    """
    의존성 주입 컨테이너

    - 각 컴포넌트는 lazy 초기화 (cached_property)
    - 테스트 시 의존성 주입 가능
    """

    settings: Settings

    # 테스트용 의존성 주입 (Optional)
    _db: Optional[DatabaseConnection] = field(default=None, repr=False)
    _router: Optional[Router] = field(default=None, repr=False)
    _sql_agent: Optional[SQLAgent] = field(default=None, repr=False)
    _rag_agent: Optional[RAGAgent] = field(default=None, repr=False)
    _hr_agent: Optional[HRAgent] = field(default=None, repr=False)

    @cached_property
    def db(self) -> DatabaseConnection:
        """DatabaseConnection 인스턴스"""
        if self._db is not None:
            return self._db
        return DatabaseConnection(
            connection_url=self.settings.DATABASE_URL,
            pool_size=self.settings.DB_POOL_SIZE,
            pool_recycle=self.settings.DB_POOL_RECYCLE,
        )

    @cached_property
    def router(self) -> Router:
        """Router 인스턴스"""
        if self._router is not None:
            return self._router

        # Provider에 따라 모델명 선택
        model = (
            self.settings.OLLAMA_MODEL
            if self.settings.LLM_PROVIDER == "ollama"
            else self.settings.LLM_MODEL
        )

        return Router(
            model=model,
            temperature=self.settings.LLM_TEMPERATURE,
            provider=self.settings.LLM_PROVIDER,
            base_url=self.settings.OLLAMA_BASE_URL,
        )

    @cached_property
    def sql_agent(self) -> SQLAgent:
        """SQLAgent 인스턴스"""
        if self._sql_agent is not None:
            return self._sql_agent

        # Provider에 따라 모델명 선택
        model = (
            self.settings.OLLAMA_MODEL
            if self.settings.LLM_PROVIDER == "ollama"
            else self.settings.LLM_MODEL
        )

        return SQLAgent(
            db=self.db,
            model=model,
            max_attempts=self.settings.SQL_AGENT_MAX_ATTEMPTS,
            provider=self.settings.LLM_PROVIDER,
            base_url=self.settings.OLLAMA_BASE_URL,
        )

    @cached_property
    def rag_agent(self) -> RAGAgent:
        """RAGAgent 인스턴스"""
        if self._rag_agent is not None:
            return self._rag_agent

        # Provider에 따라 모델명 선택
        model = (
            self.settings.OLLAMA_MODEL
            if self.settings.LLM_PROVIDER == "ollama"
            else self.settings.LLM_MODEL
        )

        # RAG_EMBEDDING_PROVIDER 기반으로 임베딩 모델명 선택
        embedding_provider = self.settings.RAG_EMBEDDING_PROVIDER
        if embedding_provider == "ollama":
            embedding_model = self.settings.OLLAMA_EMBEDDING_MODEL
        elif embedding_provider == "huggingface":
            embedding_model = "dragonkue/snowflake-arctic-embed-l-v2.0-ko"
        else:
            embedding_model = self.settings.RAG_EMBEDDING_MODEL

        return RAGAgent(
            model=model,
            temperature=self.settings.LLM_TEMPERATURE,
            top_k=self.settings.RAG_TOP_K,
            embedding_model=embedding_model,
            index_path=self.settings.RAG_INDEX_PATH,
            provider=self.settings.LLM_PROVIDER,
            base_url=self.settings.OLLAMA_BASE_URL,
            retriever_type=self.settings.RAG_RETRIEVER_TYPE,
            embedding_provider=embedding_provider,
            opensearch_url=self.settings.OPENSEARCH_URL,
            opensearch_index_name=self.settings.OPENSEARCH_INDEX_NAME,
            opensearch_pipeline_name=self.settings.OPENSEARCH_PIPELINE_NAME,
            opensearch_bm25_weight=self.settings.OPENSEARCH_BM25_WEIGHT,
            opensearch_knn_weight=self.settings.OPENSEARCH_KNN_WEIGHT,
        )

    @cached_property
    def hr_agent(self) -> HRAgent:
        """HRAgent 인스턴스"""
        if self._hr_agent is not None:
            return self._hr_agent
        return HRAgent(
            router=self.router,
            sql_agent=self.sql_agent,
            rag_agent=self.rag_agent,
            verbose=self.settings.DEBUG,
        )


# 전역 컨테이너 (FastAPI lifespan에서 초기화)
_container: Optional[Container] = None


def init_container(settings: Optional[Settings] = None) -> Container:
    """
    컨테이너 초기화

    Args:
        settings: Settings 인스턴스 (None이면 기본값 사용)

    Returns:
        Container 인스턴스
    """
    global _container
    _container = Container(settings=settings or get_settings())
    return _container


def get_container() -> Container:
    """
    컨테이너 반환 (초기화 필수)

    Raises:
        RuntimeError: 컨테이너가 초기화되지 않은 경우
    """
    if _container is None:
        raise RuntimeError("Container not initialized. Call init_container() first.")
    return _container
