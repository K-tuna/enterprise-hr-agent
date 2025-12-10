"""
RAG Agent - 회사 규정 검색 및 답변 생성

사용법:
    from core.rag_agent import RAGAgent
    
    agent = RAGAgent(model="gpt-4o-mini")
    result = agent.query("연차는 몇일인가요?")
    print(result["answer"])
"""

import os
from pathlib import Path
from typing import Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class RAGAgent:
    """
    RAG Agent 클래스
    - FAISS 기반 벡터 검색
    - OpenAI LLM 답변 생성
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
        top_k: int = 3,
        index_path: str = None
    ):
        """
        Args:
            model: OpenAI 모델명
            temperature: LLM temperature (0=결정적)
            top_k: 검색할 상위 k개 문서
            index_path: FAISS 인덱스 경로 (None이면 기본 경로)
        """
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        
        # 인덱스 경로 설정
        if index_path is None:
            project_root = Path(__file__).parent.parent
            self.index_path = project_root / "data" / "faiss_index"
        else:
            self.index_path = Path(index_path)
        
        # 컴포넌트 초기화
        self._init_components()
        
    def _init_components(self):
        """벡터스토어 및 RAG Chain 초기화"""
        # Embeddings
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # FAISS 인덱스 로드
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {self.index_path}. "
                "Please run exp_06_faiss_index.py first."
            )
        
        self.vectorstore = FAISS.load_local(
            str(self.index_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.top_k}
        )
        
        # LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature
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
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _format_docs(self, docs) -> str:
        """검색된 문서를 문자열로 포맷팅"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        질문에 대한 답변 생성
        
        Args:
            question: 사용자 질문
            
        Returns:
            {
                "question": str,
                "answer": str,
                "source_docs": List[str],  # 참조 문서
                "success": bool
            }
        """
        try:
            # 검색
            source_docs = self.retriever.invoke(question)
            
            # 답변 생성
            answer = self.rag_chain.invoke(question)
            
            return {
                "question": question,
                "answer": answer,
                "source_docs": [doc.page_content[:200] for doc in source_docs],
                "success": True
            }
        
        except Exception as e:
            return {
                "question": question,
                "answer": None,
                "source_docs": [],
                "success": False,
                "error": str(e)
            }
    
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


# 편의 함수
def create_rag_agent(
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    top_k: int = 3
) -> RAGAgent:
    """
    RAGAgent 인스턴스 생성 헬퍼 함수
    
    Returns:
        RAGAgent 인스턴스
    """
    return RAGAgent(model=model, temperature=temperature, top_k=top_k)

