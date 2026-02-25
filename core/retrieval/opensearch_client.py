"""
OpenSearch Hybrid Search Client

BM25(Nori) + kNN 하이브리드 검색을 지원하는 OpenSearch 클라이언트.
Search Pipeline으로 점수 정규화(min_max) 및 가중 평균(arithmetic_mean)을 수행.

사용법:
    client = OpenSearchHybridClient(
        opensearch_url="http://localhost:9200",
        index_name="hr_documents",
        pipeline_name="hr-hybrid-pipeline",
        embeddings=embeddings,
        bm25_weight=0.6,
        knn_weight=0.4,
    )
    retriever = client.get_retriever(k=5)
    docs = retriever.invoke("연차 휴가 며칠?")
"""

import logging
from typing import List

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import chain
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

logger = logging.getLogger(__name__)

# 임베딩 벡터 차원 (snowflake-arctic-embed-l-v2.0-ko)
EMBEDDING_DIM = 1024


class OpenSearchHybridClient:
    """OpenSearch 네이티브 Hybrid Search (BM25 Nori + kNN) 클라이언트."""

    def __init__(
        self,
        opensearch_url: str,
        index_name: str,
        pipeline_name: str,
        embeddings: Embeddings,
        bm25_weight: float = 0.6,
        knn_weight: float = 0.4,
    ):
        self.index_name = index_name
        self.pipeline_name = pipeline_name
        self.embeddings = embeddings
        self.bm25_weight = bm25_weight
        self.knn_weight = knn_weight

        self.client = OpenSearch(
            hosts=[opensearch_url],
            use_ssl=False,
            verify_certs=False,
        )

    # ── 인덱스 관리 ──────────────────────────────────────────

    def create_index(self, delete_if_exists: bool = False) -> None:
        """인덱스 생성 (Nori 분석기 + kNN 벡터)."""
        if self.client.indices.exists(index=self.index_name):
            if delete_if_exists:
                self.client.indices.delete(index=self.index_name)
                logger.info("기존 인덱스 '%s' 삭제", self.index_name)
            else:
                logger.info("인덱스 '%s' 이미 존재", self.index_name)
                return

        index_body = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "nori_analyzer": {
                            "type": "custom",
                            "tokenizer": "nori_tokenizer",
                        }
                    }
                },
                "index.knn": True,
            },
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "nori_analyzer",
                    },
                    "content_embedding": {
                        "type": "knn_vector",
                        "dimension": EMBEDDING_DIM,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene",
                        },
                    },
                    "metadata": {
                        "properties": {
                            "source": {"type": "keyword"},
                            "page": {"type": "integer"},
                            "chunk_id": {"type": "keyword"},
                        }
                    },
                }
            },
        }

        self.client.indices.create(index=self.index_name, body=index_body)
        logger.info("인덱스 '%s' 생성 완료", self.index_name)

    def create_search_pipeline(self) -> None:
        """Search Pipeline 생성 (min_max 정규화 + 가중 평균)."""
        pipeline_body = {
            "description": f"HR hybrid search pipeline (BM25={self.bm25_weight}, kNN={self.knn_weight})",
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {
                                "weights": [self.bm25_weight, self.knn_weight]
                            },
                        },
                    }
                }
            ],
        }

        self.client.transport.perform_request(
            "PUT",
            f"/_search/pipeline/{self.pipeline_name}",
            body=pipeline_body,
        )
        logger.info(
            "Search Pipeline '%s' 생성 (BM25=%.0f%%, kNN=%.0f%%)",
            self.pipeline_name,
            self.bm25_weight * 100,
            self.knn_weight * 100,
        )

    def bulk_index(self, documents: List[Document]) -> tuple[int, int]:
        """문서 bulk 인덱싱 (임베딩 생성 포함).

        Args:
            documents: LangChain Document 리스트

        Returns:
            (성공 수, 실패 수)
        """
        actions = []
        total = len(documents)

        for i, doc in enumerate(documents):
            vector = self.embeddings.embed_query(doc.page_content)
            metadata = doc.metadata or {}

            action = {
                "_index": self.index_name,
                "_id": i,
                "_source": {
                    "content": doc.page_content,
                    "content_embedding": vector,
                    "metadata": {
                        "source": metadata.get("source", ""),
                        "page": metadata.get("page", 0),
                        "chunk_id": f"chunk_{i}",
                    },
                },
            }
            actions.append(action)

            if (i + 1) % 10 == 0 or (i + 1) == total:
                logger.info("임베딩 생성: %d/%d", i + 1, total)

        success, errors = bulk(self.client, actions)
        failed = len(errors) if isinstance(errors, list) else 0

        # 인덱스 리프레시
        self.client.indices.refresh(index=self.index_name)

        logger.info("Bulk 인덱싱 완료: %d 성공, %d 실패", success, failed)
        return success, failed

    # ── 검색 ─────────────────────────────────────────────────

    def hybrid_search(self, query: str, k: int = 5) -> List[Document]:
        """하이브리드 검색 (BM25 + kNN).

        Args:
            query: 검색 쿼리
            k: 반환할 문서 수

        Returns:
            LangChain Document 리스트
        """
        query_embedding = self.embeddings.embed_query(query)

        body = {
            "size": k,
            "query": {
                "hybrid": {
                    "queries": [
                        {"match": {"content": {"query": query}}},
                        {
                            "knn": {
                                "content_embedding": {
                                    "vector": query_embedding,
                                    "k": k,
                                }
                            }
                        },
                    ]
                }
            },
        }

        response = self.client.search(
            index=self.index_name,
            body=body,
            params={"search_pipeline": self.pipeline_name},
        )

        docs = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            metadata = source.get("metadata", {})
            metadata["score"] = hit["_score"]
            docs.append(
                Document(page_content=source["content"], metadata=metadata)
            )

        return docs

    def get_retriever(self, k: int = 5):
        """LangChain LCEL 호환 Retriever 반환.

        @chain 데코레이터로 Runnable을 반환하여
        기존 `retriever | format_docs` 체인과 호환.
        """

        @chain
        def retriever(query: str) -> List[Document]:
            return self.hybrid_search(query, k=k)

        return retriever

    # ── 유틸리티 ─────────────────────────────────────────────

    def health_check(self) -> bool:
        """OpenSearch 클러스터 상태 확인."""
        try:
            info = self.client.info()
            logger.info(
                "OpenSearch %s 연결 확인 (클러스터: %s)",
                info["version"]["number"],
                info["cluster_name"],
            )
            return True
        except Exception as e:
            logger.error("OpenSearch 연결 실패: %s", e)
            return False

    def get_document_count(self) -> int:
        """인덱싱된 문서 수 반환."""
        try:
            count = self.client.count(index=self.index_name)
            return count["count"]
        except Exception:
            return 0
