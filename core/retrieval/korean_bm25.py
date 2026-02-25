"""Korean BM25 Retriever with Kiwi morphological analyzer.

BM25는 기본적으로 공백 기반 토큰화를 사용하는데, 한국어는 교착어 특성상
형태소 분석 없이는 검색 성능이 크게 저하됨.

예시:
- 공백 기반: "연차휴가" → ["연차휴가"] (1토큰)
- 형태소 분석: "연차휴가를 신청합니다" → ["연차", "휴가", "신청"] (핵심 토큰만)
"""

from typing import List

from kiwipiepy import Kiwi
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

# Kiwi 인스턴스 (싱글톤)
_kiwi = None


def _get_kiwi() -> Kiwi:
    """Kiwi 인스턴스 반환 (lazy initialization)."""
    global _kiwi
    if _kiwi is None:
        _kiwi = Kiwi()
    return _kiwi


def korean_tokenizer(text: str) -> List[str]:
    """한국어 형태소 분석 토크나이저.

    명사, 동사, 형용사만 추출하여 불용어를 자동 제거.

    Args:
        text: 토큰화할 한국어 텍스트

    Returns:
        형태소 분석된 토큰 리스트

    Example:
        >>> korean_tokenizer("연차휴가를 신청하고 싶습니다")
        ['연차', '휴가', '신청']
    """
    kiwi = _get_kiwi()
    tokens = kiwi.tokenize(text)

    # 의미있는 품사만 추출
    # NNG: 일반명사, NNP: 고유명사, VV: 동사, VA: 형용사
    meaningful_tags = ('NNG', 'NNP', 'VV', 'VA')

    return [token.form for token in tokens if token.tag in meaningful_tags]


def create_korean_bm25_retriever(
    documents: List[Document],
    k: int = 10
) -> BM25Retriever:
    """한국어 최적화 BM25 Retriever 생성.

    Kiwi 형태소 분석기를 사용하여 한국어 검색 성능을 크게 향상.

    Args:
        documents: 검색 대상 문서 리스트
        k: 반환할 최대 문서 수 (기본값: 10)

    Returns:
        한국어 최적화된 BM25Retriever 인스턴스

    Example:
        >>> from langchain_core.documents import Document
        >>> docs = [Document(page_content="연차휴가는 15일입니다.")]
        >>> retriever = create_korean_bm25_retriever(docs, k=5)
        >>> results = retriever.invoke("연차 며칠?")
    """
    retriever = BM25Retriever.from_documents(
        documents,
        preprocess_func=korean_tokenizer,
        k=k
    )
    return retriever
