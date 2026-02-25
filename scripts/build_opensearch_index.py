#!/usr/bin/env python
"""
OpenSearch 하이브리드 인덱스 빌드 스크립트

PDF → 청킹 → 임베딩 → OpenSearch 인덱싱 (BM25 Nori + kNN)

사용법:
    python scripts/build_opensearch_index.py              # 기본 실행
    python scripts/build_opensearch_index.py --rebuild     # 인덱스 재생성
    python scripts/build_opensearch_index.py --test        # 검색 테스트만
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from pdfplumber import open as pdfopen
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.llm.factory import create_embeddings
from core.retrieval.opensearch_client import OpenSearchHybridClient

# OpenMP 충돌 방지 (Windows)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(args=None):
    """환경변수에서 설정 로드"""
    load_dotenv(PROJECT_ROOT / ".env")

    return {
        "provider": getattr(args, "provider", None) or os.getenv("EMBEDDING_PROVIDER", "huggingface"),
        "embedding_model": getattr(args, "model", None) or os.getenv(
            "EMBEDDING_MODEL", "dragonkue/snowflake-arctic-embed-l-v2.0-ko"
        ),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "docs_path": PROJECT_ROOT / "data" / "company_docs",
        "opensearch_url": os.getenv("OPENSEARCH_URL", "http://localhost:9200"),
        "index_name": os.getenv("OPENSEARCH_INDEX_NAME", "hr_documents"),
        "pipeline_name": os.getenv("OPENSEARCH_PIPELINE_NAME", "hr-hybrid-pipeline"),
        "bm25_weight": float(os.getenv("OPENSEARCH_BM25_WEIGHT", "0.6")),
        "knn_weight": float(os.getenv("OPENSEARCH_KNN_WEIGHT", "0.4")),
    }


def load_documents(source_path: Path) -> list[Document]:
    """PDF 문서 로드"""
    documents = []

    if source_path.is_file():
        files = [source_path]
    else:
        files = list(source_path.glob("*.pdf"))

    for file_path in files:
        logger.info("로드 중: %s", file_path.name)
        with pdfopen(str(file_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={"source": file_path.name, "page": i},
                        )
                    )

    logger.info("총 %d 페이지 로드 완료", len(documents))
    return documents


def chunk_documents(
    documents: list[Document], chunk_size: int = 1500, overlap: int = 300
) -> list[Document]:
    """문서 청킹"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info("총 %d 청크 생성", len(chunks))
    return chunks


def create_client(config: dict) -> OpenSearchHybridClient:
    """OpenSearch 클라이언트 생성"""
    embeddings = create_embeddings(
        provider=config["provider"],
        model=config["embedding_model"],
        base_url=config["base_url"] if config["provider"] == "ollama" else None,
    )

    return OpenSearchHybridClient(
        opensearch_url=config["opensearch_url"],
        index_name=config["index_name"],
        pipeline_name=config["pipeline_name"],
        embeddings=embeddings,
        bm25_weight=config["bm25_weight"],
        knn_weight=config["knn_weight"],
    )


def test_search(client: OpenSearchHybridClient):
    """검색 품질 테스트"""
    test_queries = [
        "연차휴가 일수",
        "급여 지급일",
        "출산휴가 기간",
        "성과급 기준",
    ]

    print("\n" + "=" * 60)
    print("OpenSearch Hybrid Search 테스트")
    print(f"인덱스: {client.index_name} ({client.get_document_count()} docs)")
    print("=" * 60)

    for query in test_queries:
        results = client.hybrid_search(query, k=3)
        print(f"\n[Q] {query}")
        for i, doc in enumerate(results, 1):
            score = doc.metadata.get("score", 0)
            content = doc.page_content[:100].replace("\n", " ")
            print(f"  [{i}] ({score:.4f}) {content}...")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="OpenSearch 인덱스 빌드")
    parser.add_argument("--source", type=str, help="소스 PDF 경로")
    parser.add_argument("--rebuild", action="store_true", help="인덱스 삭제 후 재생성")
    parser.add_argument("--test", action="store_true", help="검색 테스트만 실행")
    parser.add_argument("--chunk-size", type=int, default=1500)
    parser.add_argument("--overlap", type=int, default=300)
    parser.add_argument("--provider", type=str, default=None)
    parser.add_argument("--model", type=str, default=None)
    args = parser.parse_args()

    config = load_config(args)

    if args.source:
        config["docs_path"] = Path(args.source)

    logger.info("Provider: %s", config["provider"])
    logger.info("Embedding: %s", config["embedding_model"])
    logger.info("OpenSearch: %s", config["opensearch_url"])

    # 클라이언트 생성
    client = create_client(config)

    # 연결 확인
    if not client.health_check():
        logger.error("OpenSearch 연결 실패. docker-compose up opensearch -d 를 실행하세요.")
        sys.exit(1)

    # 테스트만 실행
    if args.test:
        test_search(client)
        return

    # 전체 파이프라인: 인덱스 생성 → 문서 로드 → 청킹 → 인덱싱 → Search Pipeline → 테스트
    client.create_index(delete_if_exists=args.rebuild)
    client.create_search_pipeline()

    documents = load_documents(config["docs_path"])
    chunks = chunk_documents(documents, chunk_size=args.chunk_size, overlap=args.overlap)

    success, failed = client.bulk_index(chunks)
    logger.info("인덱싱 결과: %d 성공, %d 실패", success, failed)

    # 자동 테스트
    test_search(client)

    logger.info("완료!")


if __name__ == "__main__":
    main()
