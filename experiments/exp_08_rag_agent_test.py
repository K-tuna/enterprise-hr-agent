# %%
# 셀 1: 환경 설정
"""
core/rag_agent.py 테스트
프로덕션 코드 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.rag_agent import RAGAgent

print("[OK] 환경 설정 완료")

# %%
# 셀 2: RAGAgent 초기화
"""
기본 설정으로 에이전트 생성
"""

agent = RAGAgent(model="gpt-4o-mini", temperature=0, top_k=3)

print("[OK] RAGAgent 초기화 완료")
print(f"모델: {agent.model}")
print(f"Top-K: {agent.top_k}")
print(f"인덱스 경로: {agent.index_path}")

# %%
# 셀 3: 단일 질의 테스트
"""
간단한 질문으로 동작 확인
"""

result = agent.query("연차휴가는 몇일인가요?")

print(f"[성공 여부] {result['success']}")
print(f"[질문] {result['question']}")
print(f"[답변] {result['answer']}")
print(f"\n[참조 문서 수] {len(result['source_docs'])}")
print(f"[첫 번째 참조] {result['source_docs'][0][:150]}...")

# %%
# 셀 4: 다양한 질문 테스트
"""
여러 카테고리의 질문 테스트
"""

test_cases = [
    "급여는 언제 지급되나요?",
    "초과근무 수당은 통상임금의 몇 배인가요?",
    "출산휴가는 며칠인가요?",
    "인사 평가는 연 몇회 하나요?",
    "식대는 얼마인가요?",
    "경조휴가 중 본인 결혼은 며칠인가요?",
    "자기계발비는 얼마나 지원되나요?"
]

print("=== 다양한 질문 테스트 ===\n")
success_count = 0

for question in test_cases:
    result = agent.query(question)
    if result['success']:
        success_count += 1
        print(f"✓ [Q] {question}")
        print(f"  [A] {result['answer']}\n")
    else:
        print(f"✗ [Q] {question}")
        print(f"  [ERROR] {result.get('error', 'Unknown')}\n")

print(f"성공률: {success_count}/{len(test_cases)} = {success_count/len(test_cases)*100:.0f}%")

# %%
# 셀 5: 규정에 없는 내용 질문
"""
RAG가 없는 내용을 잘 거부하는지 확인
"""

irrelevant_questions = [
    "회사의 주가는 얼마인가요?",
    "내일 날씨는 어떤가요?",
    "CEO의 이름은 무엇인가요?"
]

print("=== 규정 외 질문 테스트 ===\n")
for question in irrelevant_questions:
    result = agent.query(question)
    print(f"[Q] {question}")
    print(f"[A] {result['answer']}\n")

# %%
# 셀 6: 스트리밍 테스트
"""
스트리밍 응답 확인
"""

print("=== 스트리밍 테스트 ===")
question = "유연근무제는 어떻게 운영되나요?"
print(f"[질문] {question}")
print(f"[답변] ", end="")

for chunk in agent.stream(question):
    print(chunk, end="", flush=True)
print("\n")

# %%
# 셀 7: 성능 체크 (간단)
"""
응답 시간 측정
"""

import time

question = "연차는 몇일인가요?"
start = time.time()
result = agent.query(question)
elapsed = time.time() - start

print(f"[성능 체크]")
print(f"질문: {question}")
print(f"응답 시간: {elapsed:.2f}초")
print(f"답변 길이: {len(result['answer'])} 글자")
print(f"답변: {result['answer']}")

print("\n[OK] RAGAgent 테스트 완료!")
print("프로덕션 준비 완료 ✓")

# %%

