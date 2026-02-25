#!/usr/bin/env python
"""
FAISS 벡터 인덱스 빌드 스크립트

사용법:
    python scripts/build_index.py                     # 기본 실행 (HuggingFace snowflake-ko)
    python scripts/build_index.py --test              # 검색 테스트만
    python scripts/build_index.py --source file.pdf   # 특정 파일
    python scripts/build_index.py --provider huggingface --model dragonkue/snowflake-arctic-embed-l-v2.0-ko
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
from langchain_community.vectorstores import FAISS

from core.llm.factory import create_embeddings

# OpenMP 충돌 방지 (Windows)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def load_config(args=None):
    """환경변수에서 설정 로드 (CLI 인자 우선)"""
    load_dotenv(PROJECT_ROOT / ".env")

    # CLI 인자 우선, 없으면 환경변수, 없으면 기본값
    provider = getattr(args, 'provider', None) or os.getenv("EMBEDDING_PROVIDER", "huggingface")
    model = getattr(args, 'model', None) or os.getenv("EMBEDDING_MODEL", "dragonkue/snowflake-arctic-embed-l-v2.0-ko")

    return {
        "provider": provider,
        "embedding_model": model,
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "docs_path": PROJECT_ROOT / "data" / "company_docs",
        "index_path": PROJECT_ROOT / "data" / "faiss_index",
    }


def load_documents(source_path: Path) -> list[Document]:
    """PDF 문서 로드"""
    documents = []

    if source_path.is_file():
        files = [source_path]
    else:
        files = list(source_path.glob("*.pdf"))

    for file_path in files:
        logger.info(f"로드 중: {file_path.name}")
        with pdfopen(str(file_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": file_path.name, "page": i}
                    ))

    logger.info(f"총 {len(documents)} 페이지 로드 완료")
    return documents


def chunk_documents(documents: list[Document], chunk_size: int = 1500, overlap: int = 300) -> list[Document]:
    """문서 청킹"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"총 {len(chunks)} 청크 생성")
    return chunks


def build_index(chunks: list[Document], config: dict) -> FAISS:
    """FAISS 인덱스 생성"""
    logger.info(f"임베딩 모델: {config['provider']}/{config['embedding_model']}")

    embeddings = create_embeddings(
        provider=config["provider"],
        model=config["embedding_model"],
        base_url=config["base_url"] if config["provider"] == "ollama" else None
    )

    # 임베딩 테스트
    test_vec = embeddings.embed_query("테스트")
    logger.info(f"벡터 차원: {len(test_vec)}")

    # 인덱스 생성
    logger.info("인덱스 생성 중... (시간 소요)")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    return vectorstore


def save_index(vectorstore: FAISS, index_path: Path):
    """인덱스 저장"""
    index_path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_path))
    logger.info(f"인덱스 저장 완료: {index_path}")


def test_search(index_path: Path, config: dict):
    """검색 품질 테스트"""
    logger.info("검색 테스트 시작")

    embeddings = create_embeddings(
        provider=config["provider"],
        model=config["embedding_model"],
        base_url=config["base_url"] if config["provider"] == "ollama" else None
    )

    vectorstore = FAISS.load_local(
        str(index_path),
        embeddings,
        allow_dangerous_deserialization=True
    )

    test_queries = [
        "연차휴가 일수",
        "급여 지급일",
        "출산휴가 기간",
        "성과급 기준"
    ]

    print("\n" + "=" * 60)
    print("검색 품질 테스트")
    print("=" * 60)

    for query in test_queries:
        results = vectorstore.similarity_search(query, k=1)
        content = results[0].page_content[:100].replace("\n", " ")
        print(f"\n[Q] {query}")
        print(f"[A] {content}...")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="FAISS 인덱스 빌드")
    parser.add_argument("--source", type=str, help="소스 PDF 경로 (기본: data/company_docs/)")
    parser.add_argument("--output", type=str, help="인덱스 저장 경로 (기본: data/faiss_index/)")
    parser.add_argument("--test", action="store_true", help="검색 테스트만 실행")
    parser.add_argument("--chunk-size", type=int, default=1500, help="청크 크기 (기본: 1500)")
    parser.add_argument("--overlap", type=int, default=300, help="청크 오버랩 (기본: 300)")
    parser.add_argument("--provider", type=str, default="huggingface",
                        help="임베딩 provider (openai/ollama/huggingface)")
    parser.add_argument("--model", type=str,
                        default="dragonkue/snowflake-arctic-embed-l-v2.0-ko",
                        help="임베딩 모델명")
    args = parser.parse_args()

    config = load_config(args)

    if args.source:
        config["docs_path"] = Path(args.source)
    if args.output:
        config["index_path"] = Path(args.output)

    logger.info(f"Provider: {config['provider']}")
    logger.info(f"Embedding: {config['embedding_model']}")

    if args.test:
        test_search(config["index_path"], config)
        return

    # 전체 파이프라인
    documents = load_documents(config["docs_path"])
    chunks = chunk_documents(documents, chunk_size=args.chunk_size, overlap=args.overlap)
    vectorstore = build_index(chunks, config)
    save_index(vectorstore, config["index_path"])

    # 자동 테스트
    test_search(config["index_path"], config)

    logger.info("완료!")


if __name__ == "__main__":
    main()
