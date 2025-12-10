# %%
# 셀 1: 환경 설정
"""
FAISS 벡터 인덱스 생성 및 검색 실험
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_PATH = PROJECT_ROOT / "data" / "company_docs" / "회사규정.pdf"
INDEX_PATH = PROJECT_ROOT / "data" / "faiss_index"

print(f"[OK] 환경 설정 완료")
print(f"PDF: {DOCS_PATH.exists()}")
print(f"인덱스 저장 경로: {INDEX_PATH}")

# %%
# 셀 2: 문서 로드 및 청킹 (PDFPlumber 사용)
"""
PDFPlumber로 한글 PDF 정확히 파싱
"""

from pdfplumber import open as pdfopen
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# PDFPlumber로 PDF 로드
documents = []
with pdfopen(str(DOCS_PATH)) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            documents.append(Document(page_content=text, metadata={"page": i}))

print(f"[OK] PDF 로드 완료 (PDFPlumber)")
print(f"페이지 수: {len(documents)}")
print(f"\n=== 첫 페이지 미리보기 (200자) ===")
print(documents[0].page_content[:200])
print(f"\n=== 한글 키워드 확인 ===")
print(f"'급여' 포함: {'급여' in documents[0].page_content}")
print(f"'연차' 포함: {'연차' in documents[0].page_content}")

# 청킹
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)

print(f"\n[OK] 청킹 완료")
print(f"총 청크 수: {len(chunks)}")

# %%
# 셀 3: OpenAI Embeddings 초기화
"""
text-embedding-3-small 모델 사용 (저렴, 빠름)
"""

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=openai_api_key
)

# 테스트
test_vector = embeddings.embed_query("테스트")
print(f"[OK] Embeddings 초기화 완료")
print(f"벡터 차원: {len(test_vector)}")

# %%
# 셀 4: FAISS 인덱스 생성
"""
청크들을 임베딩하여 FAISS 인덱스 생성
"""

from langchain_community.vectorstores import FAISS

# FAISS 인덱스 생성 (시간 소요됨)
print("[INFO] FAISS 인덱스 생성 중... (20-30초 소요)")
vectorstore = FAISS.from_documents(chunks, embeddings)

print(f"[OK] FAISS 인덱스 생성 완료")
print(f"저장된 문서 수: {len(chunks)}")

# %%
# 셀 5: 인덱스 저장
"""
생성된 인덱스를 디스크에 저장 (재사용 가능)
"""

# 디렉토리 생성
INDEX_PATH.mkdir(parents=True, exist_ok=True)

# 저장
vectorstore.save_local(str(INDEX_PATH))
print(f"[OK] 인덱스 저장 완료: {INDEX_PATH}")

# %%
# 셀 6: 유사도 검색 테스트
"""
질의와 유사한 청크 검색
"""

# 테스트 질의
query = "연차휴가는 몇일인가요?"
results = vectorstore.similarity_search(query, k=3)

print(f"[검색 질의] {query}")
print(f"[검색 결과] 상위 {len(results)}개 청크\n")

for i, doc in enumerate(results):
    print(f"=== 결과 {i+1} ===")
    print(f"페이지: {doc.metadata.get('page', 'N/A')}")
    print(f"내용: {doc.page_content[:200]}...")
    print("-" * 60)

# %%
# 셀 7: 다양한 질의 테스트
"""
여러 질문으로 검색 품질 확인
"""

test_queries = [
    "급여는 언제 지급되나요?",
    "초과근무 수당은 어떻게 되나요?",
    "출산휴가 기간은?",
    "인사 평가는 언제 하나요?"
]

print("=== 다양한 질의 테스트 ===\n")
for query in test_queries:
    results = vectorstore.similarity_search(query, k=1)
    print(f"[Q] {query}")
    print(f"[A] {results[0].page_content[:150]}...")
    print()

print("[OK] FAISS 인덱스 생성 및 검색 완료!")
print("다음 단계: exp_07에서 RAG Chain 구현")

# %%

