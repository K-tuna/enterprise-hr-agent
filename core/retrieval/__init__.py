"""Retrieval module for Korean-optimized search."""

from .korean_bm25 import korean_tokenizer, create_korean_bm25_retriever

__all__ = [
    "korean_tokenizer",
    "create_korean_bm25_retriever",
    "OpenSearchHybridClient",
]


def __getattr__(name):
    """Lazy import for OpenSearchHybridClient (opensearch-py 미설치 환경 호환)."""
    if name == "OpenSearchHybridClient":
        from .opensearch_client import OpenSearchHybridClient
        return OpenSearchHybridClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
