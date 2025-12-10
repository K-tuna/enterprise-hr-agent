# %%
# 셀 1: 환경 설정
"""
RAG Chain 구현 - LCEL 스타일
검색 → 컨텍스트 생성 → LLM 답변 생성
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
INDEX_PATH = PROJECT_ROOT / "data" / "faiss_index"

print(f"[OK] 환경 설정 완료")

# %%
# 셀 2: FAISS 인덱스 로드
"""
저장된 인덱스 불러오기
"""

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.load_local(
    str(INDEX_PATH), 
    embeddings,
    allow_dangerous_deserialization=True
)

print(f"[OK] FAISS 인덱스 로드 완료")

# %%
# 셀 3: Retriever 생성
"""
검색기 설정 (k=3: 상위 3개 청크)
"""

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 테스트
test_docs = retriever.invoke("연차는 몇일?")
print(f"[OK] Retriever 생성 완료")
print(f"테스트 검색 결과: {len(test_docs)}개 문서")

# %%
# 셀 4: 프롬프트 템플릿
"""
RAG 프롬프트: 검색된 컨텍스트를 기반으로 답변
"""

from langchain_core.prompts import ChatPromptTemplate

template = """당신은 회사 인사 규정 전문가입니다.
아래 회사 규정 내용을 참고하여 질문에 정확하고 간결하게 답변하세요.

<규정 내용>
{context}
</규정 내용>

질문: {question}

답변:"""

prompt = ChatPromptTemplate.from_template(template)
print("[OK] 프롬프트 템플릿 생성 완료")

# %%
# 셀 5: RAG Chain 구성 (LCEL)
"""
Retriever → format_docs → Prompt → LLM → StrOutputParser
"""

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 문서 포맷팅 함수
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# RAG Chain (LCEL)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("[OK] RAG Chain 구성 완료")

# %%
# 셀 6: RAG Chain 테스트
"""
단일 질의 테스트
"""

question = "연차휴가는 몇일인가요?"
answer = rag_chain.invoke(question)

print(f"[질문] {question}")
print(f"[답변] {answer}")

# %%
# 셀 7: 다양한 질문 테스트
"""
여러 질문으로 RAG 성능 확인
"""

test_questions = [
    "급여는 언제 지급되나요?",
    "초과근무 수당은 통상임금의 몇 배인가요?",
    "출산휴가는 며칠인가요?",
    "인사 평가는 연 몇회 하나요?",
    "식대와 교통비는 각각 얼마인가요?",
    "경조휴가 중 본인 결혼은 며칠인가요?"
]

print("=== RAG Chain 테스트 ===\n")
for q in test_questions:
    answer = rag_chain.invoke(q)
    print(f"[Q] {q}")
    print(f"[A] {answer}\n")
    print("-" * 60)

# %%
# 셀 8: 스트리밍 테스트 (선택)
"""
스트리밍 응답 확인
"""

print("[스트리밍 테스트]")
question = "자기계발비는 얼마나 지원되나요?"
print(f"질문: {question}\n답변: ", end="")

for chunk in rag_chain.stream(question):
    print(chunk, end="", flush=True)
print("\n")

print("[OK] RAG Chain 구현 및 테스트 완료!")
print("다음 단계: core/rag_agent.py 리팩토링")

# %%

