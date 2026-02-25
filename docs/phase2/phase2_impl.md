# Phase 2: 구현 상세 가이드

> **Implementation Guide**
> 버전: 2.2
> 작성일: 2025-01-16
> 대상: 초보 개발자 (학습 병행)
> 참조: docs/phase2/phase2_prd.md (v2.2 - OpenSearch 하이브리드 서치)

---

## 1. 개요

### 1.1 목적
Phase 2 PRD에 정의된 Task를 **2025 현업 표준 패턴**으로 구현하기 위한 상세 가이드입니다.
각 Step은 **학습 → 구현 → 검증** 사이클로 구성되어 있습니다.

> **2025 현업 표준 업데이트 (v2.2)**
> - 모니터링(LangSmith)이 최우선
> - **RAG Agent 먼저** (빠르게 완료): Chunking → Hybrid(FAISS) → **OpenSearch 실험/평가** → 마이그레이션 → Reranker 순서
> - **SQL Agent 나중** (차별화 포인트): Schema → Few-shot → Masked → CoT → SQLCoder 순서
> - **OpenSearch 도입**: FAISS → OpenSearch 네이티브 hybrid query 마이그레이션 (Jupyter 실험 후 프로덕션 적용)
> - 상세 구현은 학습 노트북(`notebooks/phase2/study/`) 참조

### 1.2 구현 순서 (2025 현업 표준 기반)

```
[Phase A: 모니터링 - Observability First]
Step 1: Task 3 (LangSmith 트레이싱) ───────────────────┐
                                                        │
[Phase B: 평가 체계 - Measurement]                      │
Step 2: Task 2 (SQL 평가 버그 수정) ───────────────────┤
Step 3: Task 1 (RAG 평가 RAGAS) ───────────────────────┤
                                                        │
[Phase C: RAG Agent 고도화 - 2025 SOTA] 빠르게 완료     │
Step 4: Task 7 (Chunking 최적화) ──────────────────────┤
Step 5: Task 9 (Hybrid Search - BM25+FAISS 실험) ─────┤
Step 5.5: Task 9 (OpenSearch Hybrid 실험/평가 비교) ───┤
Step 5.6: Task 9 (OpenSearch 프로덕션 마이그레이션) ───┤
Step 6: Task 8 (Reranker) ─────────────────────────────┤
                                                        │
[Phase D: SQL Agent 고도화 - 2025 SOTA] 차별화 포인트   │
Step 7: Task 11 (Schema Enhancement) ──────────────────┤
Step 8: Task 10 (Dynamic Few-shot) ────────────────────┤
Step 9: Task 10-2 (마스크 질문 임베딩) ★신규 ──────────┤
Step 10: Task 10-3 (CoT 프롬프팅) ★신규 ───────────────┤
Step 11: Task 12 (SQLCoder - 선택적) ──────────────────┤
                                                        │
[Phase E: 보안 - Security]                              │
Step 12: Task 5 (SQL Query Validation) ────────────────┤
Step 13: Task 4 (Guardrails + PII 마스킹) ─────────────┤
                                                        │
[Phase F: UX]                                           │
Step 14: Task 13 (Streaming + 대화 히스토리) ──────────┘
```

> **노트북 가이드**: 각 Step별 학습 노트북
> - `notebooks/phase2/study/study_01_langsmith.ipynb` ~ `study_14_streaming.ipynb`
> - `notebooks/phase2/step_01_langsmith.ipynb` ~ `step_15_final_evaluation.ipynb`

### 1.3 전제 조건

| 항목 | 요구사항 | 확인 방법 |
|------|----------|----------|
| Python | 3.10+ | `python --version` |
| Ollama | 설치 및 실행 | `ollama list` |
| MySQL | 8.0+ | `docker-compose ps` |
| v1.0 코드 | 정상 동작 | `curl localhost:8000/api/v1/health` |

### 1.4 신규 의존성 추가

```bash
# requirements.txt에 추가
pip install ragas>=0.2.0 datasets>=2.0.0 langsmith>=0.1.0 \
            sqlparse>=0.5.0 rank-bm25>=0.2.0 \
            opensearch-py>=2.4.0 \
            sentence-transformers>=3.0.0 \
            sse-starlette>=1.0.0 sseclient-py>=1.0.0
```

---

## 2. Phase A: 모니터링

### Step 1: LangSmith 트레이싱 (Task 3)

#### 2.1 학습 목표
- LangSmith 개념 이해 (LLM 호출 추적/디버깅 플랫폼)
- 환경 변수 기반 자동 트레이싱
- 대시보드에서 호출 내역 확인

#### 2.2 왜 모니터링이 먼저인가?

> **Observability First**: 개선하려면 먼저 관찰할 수 있어야 합니다.
> LangSmith를 먼저 설정하면 이후 모든 실험/개선을 추적할 수 있습니다.
> - LLM 호출 지연 시간 확인
> - 프롬프트 입출력 디버깅
> - 에러 트레이스 확인

#### 2.3 LangSmith 계정 설정

1. https://smith.langchain.com 접속
2. 회원가입 (무료 플랜 사용 가능)
3. Settings → API Keys → Create API Key
4. 프로젝트 생성: `enterprise-hr-agent`

#### 2.4 환경 변수 설정

```bash
# .env 파일에 추가
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=enterprise-hr-agent
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

#### 2.5 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `app/core/config.py` | LangSmith 환경변수 추가 |

#### 2.6 Config 수정

```python
# app/core/config.py 에 추가

class Settings(BaseSettings):
    # ... 기존 설정 ...

    # === LangSmith 설정 (Phase 2) ===
    LANGCHAIN_TRACING_V2: bool = Field(
        default=False,
        description="LangSmith 트레이싱 활성화"
    )
    LANGCHAIN_API_KEY: Optional[str] = Field(
        default=None,
        description="LangSmith API 키"
    )
    LANGCHAIN_PROJECT: str = Field(
        default="enterprise-hr-agent",
        description="LangSmith 프로젝트명"
    )
    LANGCHAIN_ENDPOINT: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API 엔드포인트"
    )
```

#### 2.7 왜 이렇게 하는가?

> **자동 트레이싱**: LangChain은 `LANGCHAIN_TRACING_V2=true`만 설정하면
> 모든 LLM 호출을 자동으로 LangSmith에 기록합니다.
> 추가 코드 변경 없이 바로 작동합니다!

#### 2.8 (선택) 명시적 트레이싱 데코레이터

특정 함수에 메타데이터를 추가하고 싶다면:

```python
# 선택: 명시적 트레이싱 (메타데이터 추가 시)
from langsmith import traceable

@traceable(run_type="chain", name="hr_query", tags=["production"])
def query(self, question: str) -> AgentResult:
    # ... 기존 코드 ...
```

#### 2.9 테스트 방법

```bash
# 1. 환경변수 확인
cat .env | grep LANGCHAIN

# 2. API 호출 테스트
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

from core.agents.sql_agent import SQLAgent
from core.database.connection import DatabaseConnection

db = DatabaseConnection(os.getenv('DATABASE_URL'))
agent = SQLAgent(db=db, model='qwen3:8b', provider='ollama', base_url='http://localhost:11434')
result = agent.query('직원 수는?')
print(result)
"

# 3. LangSmith 대시보드 확인
# https://smith.langchain.com/o/<org>/projects/enterprise-hr-agent
```

#### 2.10 성공 기준

- [ ] LangSmith 대시보드에 호출 로그가 표시됨
- [ ] 각 호출의 입력/출력 확인 가능
- [ ] 소요 시간, 토큰 수 표시

---

## 3. Phase B: 평가 체계

### Step 2: SQL 평가 버그 수정 (Task 2)

#### 3.1 학습 목표
- TypedDict와 일반 dict의 차이점 이해
- AgentResult 반환 형식 분석
- 방어적 프로그래밍 (Defensive Programming)

#### 3.2 현재 버그 분석

**파일**: `scripts/evaluate_sql.py` (Line 90)

**증상**:
```
error: "'dict' object has no attribute 'metadata'"
```

**원인 분석**:
```python
# 현재 코드 (문제)
generated_sql = response.get("metadata", {}).get("sql", "")

# SQLAgent.query()가 반환하는 실제 형식 (core/agents/sql_agent.py:96-106)
return AgentResult(
    success=success,
    answer=answer,
    metadata={
        "agent_type": "SQL_AGENT",
        "sql": final["sql"],       # ← 이 값을 가져와야 함
        "results": final["results"],
        "attempts": final["attempt"],
    },
    error=final["error"],
)
```

#### 3.3 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `scripts/evaluate_sql.py` | Line 86-100 응답 파싱 로직 수정 |

#### 3.4 수정 코드

```python
# scripts/evaluate_sql.py - Line 86-100 수정

try:
    # 1. Agent로 SQL 생성
    response = agent.query(case["question"])

    # [디버깅] 실제 반환 형식 확인 (첫 실행 시 주석 해제)
    # print(f"  Response type: {type(response)}")
    # print(f"  Response keys: {response.keys() if isinstance(response, dict) else 'N/A'}")
    # print(f"  Response: {response}")

    # 2. 안전한 파싱 (TypedDict 또는 dict 모두 처리)
    if isinstance(response, dict):
        # metadata 추출
        metadata = response.get("metadata")
        if isinstance(metadata, dict):
            generated_sql = metadata.get("sql", "")
        else:
            generated_sql = ""
        success = response.get("success", False)
    else:
        # 예상치 못한 타입
        generated_sql = ""
        success = False
        print(f"  [경고] 예상치 못한 응답 타입: {type(response)}")

    # 3. 빈 SQL 처리
    if not generated_sql:
        print(f"  [경고] SQL 추출 실패")
        if not success:
            print(f"  [에러] {response.get('error', 'Unknown error')}")

    print(f"  생성된 SQL: {generated_sql[:80]}..." if generated_sql else "  생성된 SQL: (없음)")
```

#### 3.5 왜 이렇게 하는가?

> **방어적 프로그래밍**: 외부 함수의 반환값을 신뢰하지 않고, 타입과 존재 여부를 항상 확인합니다.
> TypedDict는 **타입 힌팅용**이며, 런타임에서는 일반 dict와 동일하게 동작합니다.
> 하지만 반환 형식이 예상과 다를 수 있으므로, `isinstance()` 체크를 추가합니다.

#### 3.6 테스트 방법

```bash
# 1. 단일 모델 테스트 (디버깅용)
python scripts/evaluate_sql.py --model qwen3:8b

# 2. Base vs Fine-tuned 비교
python scripts/evaluate_sql.py --compare

# 3. 예상 출력
# SQL Agent 평가 시작: qwen3:8b
# [sql_001] 직원 수는?
#   생성된 SQL: SELECT COUNT(*) FROM employees...
#   실행: 성공
#   결과 일치: 예
```

#### 3.7 성공 기준

- [ ] `'dict' object has no attribute 'metadata'` 에러 없음
- [ ] Execution Accuracy, Result Accuracy 수치가 출력됨
- [ ] 결과가 `data/finetuning/sql_eval_results.json`에 저장됨

---

### Step 3: RAG 평가 RAGAS 적용 (Task 1)

#### 3.8 학습 목표
- RAGAS 프레임워크와 4대 메트릭 이해
  - **Faithfulness**: 답변이 컨텍스트에 근거하는지 (hallucination 체크)
  - **Answer Relevancy**: 답변이 질문에 관련있는지
  - **Context Precision**: 검색된 문서 중 관련 있는 비율
  - **Context Recall**: 필요한 정보가 모두 검색됐는지
- LangChain LLM을 RAGAS에 연결하는 방법

#### 3.9 왜 RAGAS를 사용하는가?

> **현업 표준**: RAGAS는 RAG 평가의 de facto standard입니다.
> 기존 키워드 매칭 방식은 동의어를 못 잡고, LLM-as-Judge는 주관적입니다.
> RAGAS는 논문 기반의 신뢰할 수 있는 메트릭을 제공합니다.

| 기존 방식 (비표준) | RAGAS (현업 표준) |
|------------------|------------------|
| 키워드 매칭 | Faithfulness |
| LLM-as-Judge (1-5점) | Answer Relevancy |
| 없음 | Context Precision |
| 없음 | Context Recall |

#### 3.10 신규 파일

| 파일 | 설명 |
|------|------|
| `scripts/evaluate_rag_ragas.py` | RAGAS 기반 평가 스크립트 |

#### 3.11 RAGAS 데이터셋 형식

```python
# RAGAS가 요구하는 필드
{
    "question": "병가는 어떻게 사용하나요?",     # 질문
    "answer": "생성된 답변",                    # RAGAgent가 생성
    "contexts": ["검색된 문서1", "문서2", ...],  # RAGAgent가 검색
    "ground_truth": "정답 텍스트"               # 테스트셋에서 제공
}
```

#### 3.12 구현 코드

```python
# scripts/evaluate_rag_ragas.py

"""
RAG Agent 평가 (RAGAS 현업 표준)

현업 표준 출처:
- https://docs.ragas.io/
- https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# RAGAS 임포트
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall
)
from ragas.llms import LangchainLLMWrapper

# 프로젝트 임포트
from core.agents.rag_agent import RAGAgent
from core.llm.factory import create_chat_model


def convert_to_ragas_format(
    test_cases: List[Dict],
    agent: RAGAgent
) -> List[Dict[str, Any]]:
    """기존 테스트셋을 RAGAS 형식으로 변환"""
    ragas_data = []

    for i, case in enumerate(test_cases, 1):
        print(f"  [{i}/{len(test_cases)}] {case['question'][:30]}...")

        try:
            response = agent.query(case["question"])
            metadata = response.get("metadata", {})
            source_docs = metadata.get("source_docs", [])

            if source_docs and not isinstance(source_docs[0], str):
                source_docs = [str(doc) for doc in source_docs]

            ragas_data.append({
                "question": case["question"],
                "answer": response.get("answer", ""),
                "contexts": source_docs if source_docs else [""],
                "ground_truth": case.get("ground_truth", case.get("expected_answer", ""))
            })

        except Exception as e:
            print(f"    [에러] {e}")
            ragas_data.append({
                "question": case["question"],
                "answer": "",
                "contexts": [""],
                "ground_truth": case.get("ground_truth", "")
            })

    return ragas_data


def evaluate_with_ragas(
    model: str = "qwen3:8b",
    provider: str = "ollama",
    base_url: str = "http://localhost:11434",
    test_file: str = "data/finetuning/rag_test.json",
    output_file: str = "data/finetuning/ragas_results.json"
) -> Dict[str, float]:
    """RAGAS 평가 실행"""
    print(f"\n{'='*60}")
    print(f"RAGAS 평가 시작: {model}")
    print(f"{'='*60}")

    # 1. 평가자 LLM 설정
    print("\n[1/5] 평가자 LLM 초기화...")
    evaluator_llm = create_chat_model(
        provider=provider,
        model=model,
        temperature=0,
        base_url=base_url
    )
    ragas_llm = LangchainLLMWrapper(evaluator_llm)

    # 2. RAGAgent 초기화
    print("[2/5] RAG Agent 초기화...")
    agent = RAGAgent(
        model=model,
        provider=provider,
        base_url=base_url,
        top_k=3
    )

    # 3. 테스트 케이스 로드 및 변환
    print("[3/5] 테스트 데이터 변환 중...")
    test_path = project_root / test_file
    with open(test_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    ragas_data = convert_to_ragas_format(test_cases, agent)

    # 4. RAGAS 평가 실행
    print("[4/5] RAGAS 평가 실행 중... (시간이 걸릴 수 있습니다)")
    dataset = Dataset.from_list(ragas_data)

    metrics = [
        Faithfulness(llm=ragas_llm),
        AnswerRelevancy(llm=ragas_llm),
        ContextPrecision(llm=ragas_llm),
        ContextRecall(llm=ragas_llm)
    ]

    results = evaluate(dataset, metrics=metrics)

    # 5. 결과 출력
    print(f"\n{'='*60}")
    print(f"[5/5] RAGAS 평가 결과: {model}")
    print(f"{'='*60}")
    print(f"  Faithfulness:      {results['faithfulness']:.3f}")
    print(f"  Answer Relevancy:  {results['answer_relevancy']:.3f}")
    print(f"  Context Precision: {results['context_precision']:.3f}")
    print(f"  Context Recall:    {results['context_recall']:.3f}")

    avg_score = (
        results['faithfulness'] +
        results['answer_relevancy'] +
        results['context_precision'] +
        results['context_recall']
    ) / 4
    print(f"\n  종합 점수 (평균): {avg_score:.3f}")

    # 6. 결과 저장
    output_path = project_root / output_file
    result_data = {
        "model": model,
        "provider": provider,
        "metrics": {
            "faithfulness": float(results['faithfulness']),
            "answer_relevancy": float(results['answer_relevancy']),
            "context_precision": float(results['context_precision']),
            "context_recall": float(results['context_recall']),
            "average": float(avg_score)
        },
        "test_count": len(test_cases)
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {output_path}")

    return dict(results)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG Agent RAGAS 평가")
    parser.add_argument("--model", type=str, default="qwen3:8b", help="평가할 모델")
    parser.add_argument("--compare", action="store_true", help="Base vs Fine-tuned 비교")
    parser.add_argument("--provider", type=str, default="ollama")
    parser.add_argument("--base-url", type=str, default="http://localhost:11434")

    args = parser.parse_args()

    if args.compare:
        # Base vs Fine-tuned 비교 (구현 생략)
        pass
    else:
        evaluate_with_ragas(
            model=args.model,
            provider=args.provider,
            base_url=args.base_url
        )
```

#### 3.13 테스트 방법

```bash
# 1. 단일 모델 평가
python scripts/evaluate_rag_ragas.py --model qwen3:8b

# 2. Base vs Fine-tuned 비교
python scripts/evaluate_rag_ragas.py --compare

# 3. 예상 출력
# RAGAS 평가 결과: qwen3:8b
#   Faithfulness:      0.750
#   Answer Relevancy:  0.820
#   Context Precision: 0.780
#   Context Recall:    0.650
#   종합 점수 (평균):   0.750
```

#### 3.14 성공 기준

- [ ] 4개 RAGAS 메트릭이 0~1 사이 값으로 출력
- [ ] 종합 점수 >= 0.7
- [ ] 결과가 `data/finetuning/ragas_results.json`에 저장됨

---

## 4. Phase C: SQL Agent 고도화

### Step 4: Schema Enhancement (Task 11)

#### 4.1 학습 목표
- 스키마 메타데이터의 중요성 이해
- 컬럼별 한글 설명이 SQL 정확도에 미치는 영향
- FK 관계 명시의 효과

#### 4.2 왜 Schema Enhancement가 먼저인가?

> **SOTA 연구 결과**: Spider 2.0 벤치마크에서 Schema Linking 오류가 전체 오류의 **27%**를 차지합니다.
> 컬럼 설명 추가만으로 **3-5%** 정확도 향상 가능합니다.
> — [Schema-Aware Text-to-SQL](https://arxiv.org/abs/2402.01517)

#### 4.3 신규 파일

| 파일 | 설명 |
|------|------|
| `data/schema_metadata.json` | 스키마 메타데이터 파일 |

#### 4.4 스키마 메타데이터 구조

```json
{
  "employees": {
    "description": "직원 정보 테이블",
    "columns": {
      "emp_id": {
        "description": "직원 고유 ID (PK)",
        "type": "INT",
        "example": "1001"
      },
      "name": {
        "description": "직원 이름",
        "type": "VARCHAR(100)",
        "example": "김철수"
      },
      "dept_id": {
        "description": "소속 부서 ID (FK → departments.dept_id)",
        "type": "INT",
        "example": "1"
      },
      "position": {
        "description": "직급 (사원/대리/과장/부장)",
        "type": "ENUM",
        "values": ["사원", "대리", "과장", "부장"]
      },
      "hire_date": {
        "description": "입사일",
        "type": "DATE",
        "example": "2020-01-15"
      }
    },
    "relations": [
      {"from": "dept_id", "to": "departments.dept_id", "type": "FK"}
    ]
  },
  "departments": {
    "description": "부서 정보 테이블",
    "columns": {
      "dept_id": {
        "description": "부서 고유 ID (PK)",
        "type": "INT",
        "example": "1"
      },
      "name": {
        "description": "부서명",
        "type": "VARCHAR(100)",
        "example": "개발팀",
        "values": ["개발팀", "영업팀", "인사팀", "기획팀"]
      },
      "location": {
        "description": "부서 위치",
        "type": "VARCHAR(100)",
        "example": "서울 본사"
      }
    }
  },
  "salaries": {
    "description": "급여 정보 테이블",
    "columns": {
      "emp_id": {
        "description": "직원 ID (FK → employees.emp_id)",
        "type": "INT"
      },
      "base_salary": {
        "description": "기본급 (원)",
        "type": "INT",
        "example": "4000000"
      },
      "bonus": {
        "description": "보너스 (원)",
        "type": "INT",
        "example": "500000"
      }
    },
    "relations": [
      {"from": "emp_id", "to": "employees.emp_id", "type": "FK"}
    ]
  },
  "attendance": {
    "description": "근태 기록 테이블",
    "columns": {
      "emp_id": {
        "description": "직원 ID (FK → employees.emp_id)",
        "type": "INT"
      },
      "date": {
        "description": "근무일",
        "type": "DATE"
      },
      "status": {
        "description": "근태 상태",
        "type": "ENUM",
        "values": ["PRESENT", "LATE", "VACATION", "SICK_LEAVE"]
      },
      "check_in": {
        "description": "출근 시간",
        "type": "TIME"
      },
      "check_out": {
        "description": "퇴근 시간",
        "type": "TIME"
      }
    }
  }
}
```

#### 4.5 SQL Agent 프롬프트 수정

```python
# core/agents/sql_agent.py - 프롬프트에 스키마 설명 추가

def _load_schema_metadata(self) -> str:
    """스키마 메타데이터 로드 및 포맷팅"""
    import json
    from pathlib import Path

    metadata_path = Path("data/schema_metadata.json")
    if not metadata_path.exists():
        return ""

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    lines = ["=== 데이터베이스 스키마 설명 ===\n"]

    for table, info in metadata.items():
        lines.append(f"## {table}: {info.get('description', '')}")
        for col, col_info in info.get("columns", {}).items():
            desc = col_info.get("description", "")
            values = col_info.get("values", [])
            if values:
                lines.append(f"  - {col}: {desc} (값: {', '.join(values)})")
            else:
                lines.append(f"  - {col}: {desc}")
        lines.append("")

    return "\n".join(lines)

# 프롬프트 템플릿 수정
SQL_PROMPT_TEMPLATE = """
당신은 HR 데이터베이스 전문가입니다.
사용자의 질문을 분석하여 정확한 SQL 쿼리를 생성하세요.

{schema_description}

=== 데이터베이스 스키마 ===
{schema}

=== 질문 ===
{question}

=== SQL 쿼리 ===
"""
```

#### 4.6 테스트 방법

```bash
# 1. 스키마 메타데이터 로드 테스트
python -c "
from core.agents.sql_agent import SQLAgent
agent = SQLAgent(...)
print(agent._load_schema_metadata())
"

# 2. Before/After 비교
python scripts/evaluate_sql.py --model qwen3:8b  # Step 4 전
# 스키마 메타데이터 적용 후 다시 실행
python scripts/evaluate_sql.py --model qwen3:8b  # Step 4 후
```

#### 4.7 성공 기준

- [ ] 스키마 메타데이터 파일 생성 완료
- [ ] 프롬프트에 스키마 설명이 포함됨
- [ ] 정확도 +3~5% 향상

---

### Step 5: Dynamic Few-shot (Task 10)

#### 5.1 학습 목표
- 임베딩 기반 유사도 검색 이해
- Few-shot 프롬프팅 효과
- FAISS 인덱스 생성 및 검색

#### 5.2 왜 Dynamic Few-shot을 사용하는가?

> **SOTA 연구 결과**: 동적 예시 선택은 정적 예시 대비 **+19%** 정확도 향상
> — [OpenSearch-SQL (2025)](https://arxiv.org/html/2502.14913v1)

**Static vs Dynamic Few-shot:**
| 방식 | 예시 선택 | 문제점 |
|------|----------|--------|
| **Static** | 고정된 3-5개 예시 | 질문과 무관한 예시 포함 |
| **Dynamic** | 질문과 유사한 예시 검색 | ✅ 관련 예시만 사용 |

#### 5.3 신규 파일

| 파일 | 설명 |
|------|------|
| `core/sql/fewshot_index.py` | Few-shot 인덱스 관리 |
| `data/fewshot/sql_examples.faiss` | FAISS 인덱스 파일 |

#### 5.4 Few-shot 인덱스 구현

```python
# core/sql/fewshot_index.py

"""
Dynamic Few-shot 인덱스 관리

기존 sql_training.json의 질문을 임베딩하여
유사한 예시를 검색합니다.
"""

import json
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class FewshotIndex:
    """Few-shot 예시 인덱스"""

    def __init__(
        self,
        examples_path: str = "data/finetuning/sql_training.json",
        index_path: str = "data/fewshot/sql_examples",
        embedding_model = None
    ):
        """
        Args:
            examples_path: 예시 데이터 파일 경로
            index_path: FAISS 인덱스 저장 경로
            embedding_model: 임베딩 모델 (langchain embeddings)
        """
        self.examples_path = Path(examples_path)
        self.index_path = Path(index_path)
        self.embedding_model = embedding_model
        self.vectorstore: Optional[FAISS] = None
        self.examples: List[dict] = []

        self._load_or_build()

    def _load_or_build(self):
        """인덱스 로드 또는 빌드"""
        index_file = self.index_path.with_suffix(".faiss")

        if index_file.exists():
            print(f"[FewshotIndex] 기존 인덱스 로드: {index_file}")
            self.vectorstore = FAISS.load_local(
                str(self.index_path),
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            # 예시 데이터도 로드
            with open(self.examples_path, "r", encoding="utf-8") as f:
                self.examples = json.load(f)
        else:
            print(f"[FewshotIndex] 새 인덱스 빌드 중...")
            self._build_index()

    def _build_index(self):
        """인덱스 빌드"""
        # 예시 데이터 로드
        with open(self.examples_path, "r", encoding="utf-8") as f:
            self.examples = json.load(f)

        # Document 변환 (질문 텍스트를 임베딩)
        documents = []
        for i, ex in enumerate(self.examples):
            doc = Document(
                page_content=ex["question"],
                metadata={
                    "index": i,
                    "sql": ex.get("sql", ex.get("query", "")),
                    "question": ex["question"]
                }
            )
            documents.append(doc)

        # FAISS 인덱스 생성
        self.vectorstore = FAISS.from_documents(
            documents,
            self.embedding_model
        )

        # 저장
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(str(self.index_path))
        print(f"[FewshotIndex] 인덱스 저장 완료: {self.index_path}")

    def search(self, query: str, k: int = 3) -> List[dict]:
        """
        유사한 예시 검색

        Args:
            query: 검색할 질문
            k: 반환할 예시 수

        Returns:
            [{"question": ..., "sql": ...}, ...]
        """
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search(query, k=k)

        examples = []
        for doc in results:
            examples.append({
                "question": doc.metadata["question"],
                "sql": doc.metadata["sql"]
            })

        return examples

    def format_examples(self, examples: List[dict]) -> str:
        """예시를 프롬프트 형식으로 포맷팅"""
        if not examples:
            return ""

        lines = ["다음은 유사한 질문과 SQL 예시입니다:\n"]
        for i, ex in enumerate(examples, 1):
            lines.append(f"예시 {i}:")
            lines.append(f"  질문: {ex['question']}")
            lines.append(f"  SQL: {ex['sql']}")
            lines.append("")

        return "\n".join(lines)
```

#### 5.5 SQL Agent 통합

```python
# core/agents/sql_agent.py 수정

def __init__(self, ..., use_fewshot: bool = True):
    # ... 기존 코드 ...
    self.use_fewshot = use_fewshot

    if use_fewshot:
        from core.sql.fewshot_index import FewshotIndex
        from core.llm.factory import create_embeddings

        embeddings = create_embeddings(provider=self.provider, base_url=self.base_url)
        self.fewshot_index = FewshotIndex(embedding_model=embeddings)

def _generate_sql_node(self, state: SQLAgentState) -> SQLAgentState:
    """SQL 생성 노드 (Few-shot 포함)"""
    question = state["question"]

    # Dynamic Few-shot 예시 검색
    fewshot_examples = ""
    if self.use_fewshot and hasattr(self, 'fewshot_index'):
        examples = self.fewshot_index.search(question, k=3)
        fewshot_examples = self.fewshot_index.format_examples(examples)

    # 프롬프트 생성
    prompt = self.sql_prompt.format(
        schema_description=self._load_schema_metadata(),
        schema=self.schema,
        fewshot_examples=fewshot_examples,  # 추가
        question=question
    )

    # ... SQL 생성 로직 ...
```

#### 5.6 테스트 방법

```bash
# 1. 인덱스 빌드 테스트
python -c "
from core.llm.factory import create_embeddings
from core.sql.fewshot_index import FewshotIndex

embeddings = create_embeddings(provider='ollama', base_url='http://localhost:11434')
index = FewshotIndex(embedding_model=embeddings)

# 검색 테스트
examples = index.search('개발팀 평균 급여', k=3)
print(index.format_examples(examples))
"

# 2. Before/After 비교
python scripts/evaluate_sql.py --model qwen3:8b
```

#### 5.7 성공 기준

- [ ] FAISS 인덱스 생성 완료
- [ ] 유사 예시 검색 동작
- [ ] 정확도 +10~19% 향상

---

### Step 6: 마스크 질문 임베딩 (Task 10-2) ★신규

#### 6.1 학습 목표
- 마스킹 기법의 원리 이해
- 구조적 유사도 검색의 효과
- 스키마 용어 추출 방법

#### 6.2 왜 마스크 질문 임베딩을 사용하는가?

> **SOTA 기법**: 테이블명/컬럼명을 [MASK]로 치환하면 **구조적으로 유사한** 쿼리 패턴 매칭 가능
> — [OpenSearch-SQL (2025)](https://arxiv.org/html/2502.14913v1)

**일반 임베딩 vs 마스크 임베딩:**
```
일반: "개발팀 평균 급여는?" → "영업팀 총 인원은?" (낮은 유사도)
마스크: "[MASK] 평균 [MASK]는?" → "[MASK] 총 [MASK]는?" (높은 유사도)
```

#### 6.3 구현 코드

```python
# core/sql/masked_fewshot.py

"""
마스크 질문 임베딩 기반 Few-shot

스키마 용어(테이블명, 컬럼명, 값)를 [MASK]로 치환하여
구조적으로 유사한 쿼리 패턴을 검색합니다.
"""

import re
import json
from pathlib import Path
from typing import List, Set


def extract_schema_terms(schema_metadata_path: str = "data/schema_metadata.json") -> Set[str]:
    """
    스키마 메타데이터에서 마스킹 대상 용어 추출

    Returns:
        테이블명, 컬럼명, ENUM 값 등의 집합
    """
    terms = set()

    path = Path(schema_metadata_path)
    if not path.exists():
        return terms

    with open(path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    for table_name, table_info in metadata.items():
        # 테이블명 추가
        terms.add(table_name)

        for col_name, col_info in table_info.get("columns", {}).items():
            # 컬럼명 추가
            terms.add(col_name)

            # ENUM 값 추가
            for value in col_info.get("values", []):
                terms.add(value)

            # 예시 값 추가
            if "example" in col_info:
                terms.add(str(col_info["example"]))

    return terms


def mask_question(question: str, schema_terms: Set[str]) -> str:
    """
    질문에서 스키마 용어를 [MASK]로 치환

    Args:
        question: 원본 질문
        schema_terms: 마스킹 대상 용어 집합

    Returns:
        마스킹된 질문
    """
    masked = question

    # 긴 용어부터 치환 (부분 매칭 방지)
    sorted_terms = sorted(schema_terms, key=len, reverse=True)

    for term in sorted_terms:
        if len(term) < 2:  # 너무 짧은 용어 제외
            continue
        # 대소문자 무시 치환
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        masked = pattern.sub("[MASK]", masked)

    return masked


class MaskedFewshotIndex:
    """마스크 질문 기반 Few-shot 인덱스"""

    def __init__(
        self,
        examples_path: str = "data/finetuning/sql_training.json",
        index_path: str = "data/fewshot/sql_masked_examples",
        embedding_model = None
    ):
        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document

        self.examples_path = Path(examples_path)
        self.index_path = Path(index_path)
        self.embedding_model = embedding_model
        self.schema_terms = extract_schema_terms()
        self.examples = []
        self.vectorstore = None

        self._load_or_build()

    def _load_or_build(self):
        """인덱스 로드 또는 빌드"""
        index_file = self.index_path.with_suffix(".faiss")

        if index_file.exists():
            from langchain_community.vectorstores import FAISS
            self.vectorstore = FAISS.load_local(
                str(self.index_path),
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            with open(self.examples_path, "r", encoding="utf-8") as f:
                self.examples = json.load(f)
        else:
            self._build_index()

    def _build_index(self):
        """마스크된 질문으로 인덱스 빌드"""
        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document

        with open(self.examples_path, "r", encoding="utf-8") as f:
            self.examples = json.load(f)

        documents = []
        for i, ex in enumerate(self.examples):
            # 질문 마스킹
            masked_q = mask_question(ex["question"], self.schema_terms)

            doc = Document(
                page_content=masked_q,  # 마스크된 질문으로 임베딩
                metadata={
                    "index": i,
                    "original_question": ex["question"],
                    "masked_question": masked_q,
                    "sql": ex.get("sql", ex.get("query", ""))
                }
            )
            documents.append(doc)

        self.vectorstore = FAISS.from_documents(documents, self.embedding_model)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(str(self.index_path))

    def search(self, query: str, k: int = 3) -> List[dict]:
        """마스크된 쿼리로 유사 예시 검색"""
        if self.vectorstore is None:
            return []

        # 쿼리도 마스킹
        masked_query = mask_question(query, self.schema_terms)

        results = self.vectorstore.similarity_search(masked_query, k=k)

        examples = []
        for doc in results:
            examples.append({
                "question": doc.metadata["original_question"],
                "sql": doc.metadata["sql"],
                "masked": doc.metadata["masked_question"]
            })

        return examples
```

#### 6.4 테스트 방법

```bash
# 1. 마스킹 테스트
python -c "
from core.sql.masked_fewshot import extract_schema_terms, mask_question

terms = extract_schema_terms()
print('스키마 용어:', terms)

questions = [
    '개발팀 평균 급여는?',
    '영업팀 직원 수는?',
    '김철수의 입사일은?',
]

for q in questions:
    masked = mask_question(q, terms)
    print(f'{q} -> {masked}')
"

# 2. 검색 비교 테스트
python -c "
from core.llm.factory import create_embeddings
from core.sql.fewshot_index import FewshotIndex
from core.sql.masked_fewshot import MaskedFewshotIndex

embeddings = create_embeddings(provider='ollama')

# 일반 인덱스
normal = FewshotIndex(embedding_model=embeddings)
# 마스크 인덱스
masked = MaskedFewshotIndex(embedding_model=embeddings)

query = '기획팀 평균 급여는?'
print('일반 검색:', normal.search(query, k=2))
print('마스크 검색:', masked.search(query, k=2))
"
```

#### 6.5 성공 기준

- [ ] 스키마 용어 추출 동작
- [ ] 질문 마스킹 정상 동작
- [ ] 마스크 인덱스 검색 동작
- [ ] 구조적으로 유사한 쿼리 매칭 확인

---

### Step 7: CoT 프롬프팅 (Task 10-3) ★신규

#### 7.1 학습 목표
- Chain of Thought (CoT) 프롬프팅 개념
- 단계별 사고 유도 방법
- 프롬프트 엔지니어링

#### 7.2 왜 CoT를 사용하는가?

> **SOTA 기법**: CoT 프롬프팅은 SQL 생성 정확도를 **+10~15%** 향상
> — [SQL-of-Thought (2025)](https://arxiv.org/pdf/2509.00581)

CoT는 LLM이 답을 바로 생성하지 않고 **단계별로 사고**하도록 유도합니다.
복잡한 SQL의 경우 테이블, 조인, 필터, 집계를 순차적으로 생각하면 정확도가 높아집니다.

#### 7.3 구현 (프롬프트 수정만 필요)

```python
# core/agents/sql_agent.py - 프롬프트 템플릿 수정

SQL_PROMPT_WITH_COT = """
당신은 HR 데이터베이스 전문가입니다.
사용자의 질문을 분석하여 정확한 SQL 쿼리를 생성하세요.

{schema_description}

=== 데이터베이스 스키마 ===
{schema}

{fewshot_examples}

=== 질문 ===
{question}

=== 단계별로 생각해보자 ===
1. 필요한 테이블:
2. 조인 조건:
3. 필터 조건 (WHERE):
4. 집계 함수 (COUNT, AVG, SUM 등):
5. 그룹화 (GROUP BY):
6. 정렬/제한 (ORDER BY, LIMIT):

=== SQL 쿼리 ===
"""
```

#### 7.4 테스트 방법

```bash
# 1. CoT 프롬프트 출력 확인
python -c "
from core.agents.sql_agent import SQLAgent

agent = SQLAgent(use_cot=True, ...)
# 프롬프트 내용 확인
"

# 2. Before/After 비교
# CoT 없이
python scripts/evaluate_sql.py --model qwen3:8b --no-cot
# CoT 있이
python scripts/evaluate_sql.py --model qwen3:8b --cot
```

#### 7.5 성공 기준

- [ ] CoT 프롬프트 템플릿 적용
- [ ] LLM이 단계별 사고 출력 확인
- [ ] 정확도 +5~15% 향상

---

### Step 8: SQLCoder (Task 12) - 선택적

#### 8.1 학습 목표
- Text-to-SQL 전용 모델 이해
- 모델 비교 실험 방법
- 프롬프트 형식 차이

#### 8.2 왜 SQLCoder를 고려하는가?

> **전용 모델 장점**: SQLCoder-8B는 GPT-4를 능가하는 SQL 생성 정확도
> — [Defog SQLCoder](https://github.com/defog-ai/sqlcoder)

**주의**: 기존 qwen3-hr (파인튜닝 모델)과 비교 실험 후 적용 여부 결정

#### 8.3 설치

```bash
# Ollama로 SQLCoder 다운로드
ollama pull mannix/defog-llama3-sqlcoder-8b
```

#### 8.4 SQLCoder 프롬프트 형식

```python
# SQLCoder는 특정 프롬프트 형식을 요구합니다

SQLCODER_PROMPT = """
### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

### Database Schema
{schema}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]
[SQL]
"""
```

#### 8.5 비교 실험

```python
# notebooks/phase2/step_08_sqlcoder_comparison.ipynb

# 세 모델 비교
# 1. qwen3:8b (Base)
# 2. qwen3-hr (Fine-tuned)
# 3. SQLCoder-8B (전용 모델)

models = [
    ("qwen3:8b", "base"),
    ("qwen3-hr", "finetuned"),
    ("mannix/defog-llama3-sqlcoder-8b", "sqlcoder"),
]

results = {}
for model, label in models:
    accuracy = evaluate_sql_agent(model=model)
    results[label] = accuracy

# 결과 기반 적용 여부 결정
```

#### 8.6 성공 기준

- [ ] SQLCoder 모델 설치 완료
- [ ] 세 모델 비교 실험 수행
- [ ] 가장 높은 정확도 모델 선택

---

## 5. Phase D: RAG Agent 고도화

### Step 9: Chunking 최적화 (Task 7)

#### 9.1 학습 목표
- 청킹 파라미터의 영향 이해
- 최적 청크 크기 찾기
- 오버랩의 역할

#### 9.2 왜 Chunking 최적화가 먼저인가?

> **현업 표준**: 최적 청크 크기는 200-300 단어, 10-20% 오버랩
> — [kapa.ai RAG Lessons](https://www.kapa.ai/blog/rag-best-practices)

청킹은 RAG 파이프라인의 **기반**입니다. 잘못된 청킹은 이후 단계(Hybrid Search, Reranker)의 효과를 감소시킵니다.

#### 9.3 현재 청킹 설정 확인

```python
# scripts/build_index.py 확인
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 현재 설정 (확인 필요)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 현재값
    chunk_overlap=50,    # 현재값
)
```

#### 9.4 최적화 실험

```python
# notebooks/phase2/step_09_chunking.ipynb

# 청킹 파라미터 실험
params = [
    {"chunk_size": 300, "chunk_overlap": 30},
    {"chunk_size": 500, "chunk_overlap": 50},
    {"chunk_size": 700, "chunk_overlap": 70},
    {"chunk_size": 1000, "chunk_overlap": 100},
]

for p in params:
    # 인덱스 재빌드
    build_index(**p)
    # RAGAS 평가
    score = evaluate_ragas()
    print(f"chunk_size={p['chunk_size']}: {score}")
```

#### 9.5 성공 기준

- [ ] 최적 청크 크기 확정
- [ ] 인덱스 재빌드 완료
- [ ] Context Precision 향상 확인

---

### Step 10: Hybrid Search (Task 9) - BM25+FAISS 실험

> **참고**: 이 Step은 BM25+FAISS EnsembleRetriever로 하이브리드 서치 개념을 실험합니다.
> Step 10.5에서 OpenSearch 네이티브 hybrid query로 전환하고 평가 비교합니다.

#### 10.1 학습 목표
- BM25 알고리즘 이해 (키워드 기반 TF-IDF 변형)
- 벡터 검색 vs 키워드 검색의 장단점
- RRF (Reciprocal Rank Fusion) 점수 융합 기법

#### 10.2 왜 Hybrid Search를 사용하는가?

| 검색 방식 | 장점 | 단점 |
|----------|------|------|
| **FAISS (벡터)** | 의미적 유사성, 동의어 처리 | 정확한 키워드 매칭 약함 |
| **BM25 (키워드)** | 정확한 키워드 매칭 | 동의어, 문맥 이해 약함 |
| **Hybrid** | 두 장점 결합 | 구현 복잡도 증가 |

> **현업 표준**: 대부분의 프로덕션 RAG 시스템은 Hybrid Search를 사용합니다.
> 다만 FAISS + rank_bm25로 직접 조립하는 것은 현업 표준이 아닙니다.
> **현업 표준은 OpenSearch/Elasticsearch 등의 네이티브 hybrid search** 사용입니다.

#### 10.3 신규 파일

| 파일 | 설명 |
|------|------|
| `core/search/__init__.py` | 패키지 초기화 |
| `core/search/bm25_retriever.py` | BM25 검색기 (FAISS 실험용) |
| `core/search/hybrid_retriever.py` | 하이브리드 검색기 (FAISS 실험용) |

#### 10.4 BM25 Retriever 구현

```python
# core/search/bm25_retriever.py

from rank_bm25 import BM25Okapi
from typing import List, Tuple, Callable
from langchain_core.documents import Document


def korean_tokenizer(text: str) -> List[str]:
    """간단한 한국어 토크나이저"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    words = text.split()
    stopwords = {'은', '는', '이', '가', '을', '를', '의', '에', '로', '으로', '와', '과'}
    tokens = [w for w in words if w not in stopwords and len(w) > 1]
    return tokens


class BM25Retriever:
    """BM25 검색기"""

    def __init__(self, documents: List[Document], tokenizer: Callable = korean_tokenizer):
        self.documents = documents
        self.tokenizer = tokenizer
        corpus = [tokenizer(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        tokenized_query = self.tokenizer(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        import numpy as np
        top_indices = np.argsort(scores)[-top_k:][::-1]

        return [(self.documents[i], float(scores[i])) for i in top_indices if scores[i] > 0]
```

#### 10.5 Hybrid Retriever 구현

```python
# core/search/hybrid_retriever.py

from typing import List, Tuple, Dict
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from core.search.bm25_retriever import BM25Retriever


def reciprocal_rank_fusion(
    rankings: List[List[Tuple[Document, float]]],
    k: int = 60
) -> List[Tuple[Document, float]]:
    """RRF 점수 융합"""
    rrf_scores: Dict[int, float] = {}
    doc_map: Dict[int, Document] = {}

    for ranking in rankings:
        for rank, (doc, _) in enumerate(ranking, start=1):
            doc_id = hash(doc.page_content)
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0
                doc_map[doc_id] = doc
            rrf_scores[doc_id] += 1 / (k + rank)

    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [(doc_map[doc_id], score) for doc_id, score in sorted_results]


class HybridRetriever:
    """하이브리드 검색기 (FAISS + BM25)"""

    def __init__(self, vectorstore: FAISS):
        self.vectorstore = vectorstore
        all_docs = self._extract_all_docs()
        self.bm25_retriever = BM25Retriever(all_docs)

    def _extract_all_docs(self) -> List[Document]:
        docs = []
        for doc_id in self.vectorstore.index_to_docstore_id.values():
            doc = self.vectorstore.docstore.search(doc_id)
            if doc and hasattr(doc, 'page_content'):
                docs.append(doc)
        return docs

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        fetch_k = top_k * 3

        # FAISS 검색
        faiss_results = self.vectorstore.similarity_search_with_score(query, k=fetch_k)
        faiss_ranking = [(doc, 1 / (1 + score)) for doc, score in faiss_results]

        # BM25 검색
        bm25_ranking = self.bm25_retriever.search(query, top_k=fetch_k)

        # RRF 융합
        fused = reciprocal_rank_fusion([faiss_ranking, bm25_ranking])

        return [doc for doc, _ in fused[:top_k]]
```

#### 10.6 성공 기준

- [ ] Hybrid Search 정상 동작
- [ ] 키워드 매칭 쿼리에서 검색 품질 개선
- [ ] RAGAS Context Precision 향상 (+5% 이상)

---

### Step 10.5: OpenSearch Hybrid 실험 및 평가 비교 (Task 9) ★신규

> **목적**: OpenSearch 네이티브 hybrid query로 FAISS 대비 동등 이상의 성능 확인
> **방식**: Docker로 OpenSearch 환경 구성 → Jupyter 노트북에서 인덱싱/검색/평가 비교
> **프로덕션 코드(core/, scripts/)는 건드리지 않음**

#### 10.5.1 학습 목표
- OpenSearch 아키텍처 (역인덱스 + 벡터 인덱스)
- Nori 한국어 형태소 분석기
- OpenSearch hybrid query (BM25 + kNN 동시 실행)
- Search Pipeline (normalization-processor)

#### 10.5.2 왜 FAISS 대신 OpenSearch인가?

| 항목 | FAISS | OpenSearch |
|------|-------|-----------|
| DB-Engines 랭킹 | 미등록 | 2위 (20.04점) |
| BM25 | 직접 구현 필요 (rank_bm25) | 내장 (Nori 한국어 분석기) |
| 점수 융합 | RRF 직접 구현 | search pipeline 내장 |
| 메타데이터 필터링 | 수동 구현 | 쿼리 DSL 내장 |
| 한국어 토크나이저 | Kiwi 직접 구현 | Nori 내장 (공식 이미지 포함) |
| 프로덕션 운영 | 파일 기반, 제한적 | 클러스터링, 모니터링, REST API |

#### 10.5.3 Docker 환경 구성

**수정 파일**: `docker-compose.yml`

```yaml
  opensearch:
    image: opensearchproject/opensearch:2.18.0
    container_name: opensearch
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
      - OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
    ports:
      - "9200:9200"
      - "9600:9600"
    volumes:
      - opensearch_data:/usr/share/opensearch/data

volumes:
  opensearch_data:
```

**수정 파일**: `requirements.txt`
```
opensearch-py>=2.4.0
```

**수정 파일**: `.env`
```
OPENSEARCH_URL=http://localhost:9200
```

**검증**:
```bash
docker-compose up opensearch -d
curl http://localhost:9200/_cat/plugins  # Nori 확인
```

#### 10.5.4 실험 노트북

**신규 파일**: `notebooks/phase2/impl/step_06_opensearch_hybrid.ipynb`

노트북 셀 구성:

1. **환경 설정** — imports, OpenSearch 연결 확인
2. **인덱스 생성** — `hr_documents` 인덱스
   ```python
   index_body = {
       "settings": {
           "analysis": {
               "analyzer": {
                   "nori_analyzer": {
                       "type": "custom",
                       "tokenizer": "nori_tokenizer"
                   }
               }
           },
           "index.knn": True
       },
       "mappings": {
           "properties": {
               "content": {"type": "text", "analyzer": "nori_analyzer"},
               "content_embedding": {
                   "type": "knn_vector",
                   "dimension": 1024,
                   "method": {"name": "hnsw", "space_type": "cosinesimil", "engine": "lucene"}
               },
               "metadata": {
                   "properties": {
                       "source": {"type": "keyword"},
                       "page": {"type": "integer"},
                       "chunk_id": {"type": "keyword"}
                   }
               }
           }
       }
   }
   ```
3. **데이터 적재** — 기존 PDF 청킹(chunk_size=1500, overlap=300) + 임베딩(snowflake-arctic-embed-l-v2.0-ko) + bulk 인덱싱
4. **Search Pipeline 생성** — BM25/kNN 점수 정규화
   ```python
   pipeline_body = {
       "description": "HR hybrid search pipeline",
       "phase_results_processors": [
           {
               "normalization-processor": {
                   "normalization": {"technique": "min_max"},
                   "combination": {"technique": "arithmetic_mean", "parameters": {"weights": [0.5, 0.5]}}
               }
           }
       ]
   }
   ```
5. **Hybrid Search 테스트** — 샘플 쿼리 동작 확인
6. **RAGAS 평가 — 3가지 retriever 비교**:
   - FAISS only (기존 baseline)
   - BM25+FAISS EnsembleRetriever (기존 best)
   - OpenSearch Hybrid (신규)
7. **가중치 Grid Search** — BM25/kNN 비율 0.0~1.0 탐색
8. **비교 테이블 + 시각화**
9. **결과 저장** → `data/finetuning/opensearch_evaluation_results.json`

#### 10.5.5 평가 조건

- 50개 테스트 케이스 (`data/finetuning/rag_test_50.json`)
- RAGAS: Context Precision, Context Recall
- 동일 임베딩 모델: `snowflake-arctic-embed-l-v2.0-ko` (1024d)
- 동일 LLM (평가자): `gpt-4o-mini`

#### 10.5.6 성공 기준

- [ ] OpenSearch Docker 정상 기동 (Nori 플러그인 확인)
- [ ] hr_documents 인덱스 생성 + 데이터 적재 완료
- [ ] Hybrid Search 쿼리 정상 동작
- [ ] RAGAS 평가: FAISS vs BM25+FAISS vs OpenSearch Hybrid 비교 테이블 작성
- [ ] **OpenSearch Hybrid >= BM25+FAISS (Avg 0.9292)** 확인
- [ ] 최적 가중치 확정

---

### Step 10.6: OpenSearch 프로덕션 마이그레이션 (Task 9) ★신규

> **전제**: Step 10.5 평가에서 OpenSearch Hybrid >= FAISS 확인 후 진행

#### 10.6.1 학습 목표
- LangChain BaseRetriever 커스텀 구현
- Feature flag 패턴 (환경변수로 retriever 전환)
- 기존 코드 영향 최소화 전략

#### 10.6.2 신규 파일

| 파일 | 설명 |
|------|------|
| `core/retrieval/opensearch_retriever.py` | LangChain 호환 OpenSearch hybrid retriever |
| `scripts/build_opensearch_index.py` | OpenSearch 인덱스 생성 + 데이터 적재 CLI |

#### 10.6.3 OpenSearch Hybrid Retriever 구현

```python
# core/retrieval/opensearch_retriever.py

from typing import List
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from opensearchpy import OpenSearch
from pydantic import Field


class OpenSearchHybridRetriever(BaseRetriever):
    """OpenSearch 네이티브 hybrid retriever (BM25 + kNN)"""

    client: OpenSearch
    index_name: str = "hr_documents"
    embedding_model: object  # HuggingFaceEmbeddings
    k: int = 5
    bm25_weight: float = 0.5
    knn_weight: float = 0.5
    pipeline_name: str = "hr-hybrid-pipeline"

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # 쿼리 임베딩 생성
        query_embedding = self.embedding_model.embed_query(query)

        # Hybrid query
        body = {
            "size": self.k,
            "query": {
                "hybrid": {
                    "queries": [
                        {"match": {"content": {"query": query}}},
                        {"knn": {"content_embedding": {"vector": query_embedding, "k": self.k}}}
                    ]
                }
            }
        }

        response = self.client.search(
            index=self.index_name,
            body=body,
            params={"search_pipeline": self.pipeline_name}
        )

        docs = []
        for hit in response["hits"]["hits"]:
            docs.append(Document(
                page_content=hit["_source"]["content"],
                metadata=hit["_source"].get("metadata", {})
            ))
        return docs
```

#### 10.6.4 인덱스 빌드 스크립트

```python
# scripts/build_opensearch_index.py

"""
OpenSearch 인덱스 생성 및 데이터 적재
기존 build_index.py의 load_documents(), chunk_documents() 재사용
"""

from opensearchpy import OpenSearch, helpers
from scripts.build_index import load_documents, chunk_documents
# ... 인덱스 생성, 임베딩, bulk 적재 로직
```

#### 10.6.5 RAG Agent 수정

```python
# core/agents/rag_agent.py 수정

class RAGAgent:
    def __init__(self, ..., retriever_type: str = None):
        self.retriever_type = retriever_type or os.getenv("RAG_RETRIEVER_TYPE", "faiss")

        if self.retriever_type == "opensearch":
            self._init_opensearch_retriever()
        else:
            self._init_faiss_retriever()  # 기존 로직

    def _init_opensearch_retriever(self):
        from core.retrieval.opensearch_retriever import OpenSearchHybridRetriever
        from opensearchpy import OpenSearch

        client = OpenSearch(hosts=[os.getenv("OPENSEARCH_URL", "http://localhost:9200")])
        self.retriever = OpenSearchHybridRetriever(
            client=client,
            embedding_model=self.embeddings,
            k=self.top_k
        )
```

#### 10.6.6 Docker Compose 업데이트

```yaml
# docker-compose.yml - api 서비스에 추가
  api:
    environment:
      - RAG_RETRIEVER_TYPE=opensearch
      - OPENSEARCH_URL=http://opensearch:9200
    depends_on:
      - opensearch
```

#### 10.6.7 성공 기준

- [ ] `python scripts/build_opensearch_index.py` → 인덱싱 완료
- [ ] `RAG_RETRIEVER_TYPE=opensearch`로 RAG Agent 정상 동작
- [ ] 기존 `RAG_RETRIEVER_TYPE=faiss`도 정상 동작 (하위호환)

---

### Step 11: Reranker (Task 8)

#### 11.1 학습 목표
- Bi-encoder vs Cross-encoder 차이
- Re-ranking 파이프라인 이해
- 모델 선택 기준

#### 11.2 왜 Reranker가 마지막인가?

> **SOTA 순서**: Hybrid Search로 **recall** 확보 후, Reranker로 **precision** 확보
> — [Superlinked VectorHub](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)

Reranker는 Cross-encoder로 **정밀 점수**를 계산하므로 **후보가 적을수록** 효과적입니다.

#### 11.3 신규 파일

| 파일 | 설명 |
|------|------|
| `core/search/reranker.py` | Cross-encoder Re-ranker |

#### 11.4 Re-ranker 구현

```python
# core/search/reranker.py

from sentence_transformers import CrossEncoder
from typing import List, Tuple, Optional
from langchain_core.documents import Document


class Reranker:
    """Cross-encoder Re-ranker"""

    _model_cache: dict = {}

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        self.model_name = model_name
        if model_name not in Reranker._model_cache:
            Reranker._model_cache[model_name] = CrossEncoder(model_name)
        self.model = Reranker._model_cache[model_name]

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 3
    ) -> List[Tuple[Document, float]]:
        if not documents or len(documents) <= top_k:
            return [(doc, 1.0) for doc in documents]

        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)

        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        return doc_scores[:top_k]


def get_reranker(model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2") -> Reranker:
    """Re-ranker 싱글톤 반환"""
    return Reranker(model_name)
```

#### 11.5 성공 기준

- [ ] Re-ranking 후 검색 품질 개선
- [ ] RAGAS Faithfulness 향상 (+10% 이상)
- [ ] 전체 응답 시간 5초 이내

---

## 6. Phase E: 보안

### Step 12: SQL Query Validation (Task 5)

#### 12.1 학습 목표
- SQL 파싱 라이브러리 (`sqlparse`) 사용법
- 화이트리스트 기반 보안 검증
- 위험 쿼리 로깅

#### 12.2 신규 파일

| 파일 | 설명 |
|------|------|
| `core/security/sql_validator.py` | SQL 검증 로직 |

#### 12.3 SQL Validator 구현

```python
# core/security/sql_validator.py

import re
import sqlparse
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class SQLValidationResult:
    valid: bool
    statement_type: str
    blocked_keywords: List[str]
    error_message: Optional[str] = None


ALLOWED_STATEMENTS = {"SELECT"}

BLOCKED_KEYWORDS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE", "REPLACE", "MERGE",
    "ALTER", "CREATE", "RENAME", "GRANT", "REVOKE",
    "EXEC", "EXECUTE", "CALL",
    "INTO OUTFILE", "INTO DUMPFILE", "LOAD_FILE", "LOAD DATA",
    "BENCHMARK", "SLEEP", "WAIT",
}


class SQLValidator:
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path) if log_path else Path("logs/blocked_queries.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def validate(self, sql: str) -> SQLValidationResult:
        if not sql or not sql.strip():
            return SQLValidationResult(False, "EMPTY", [], "빈 SQL 쿼리입니다.")

        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return SQLValidationResult(False, "INVALID", [], "SQL 파싱 실패")
        except Exception as e:
            return SQLValidationResult(False, "ERROR", [], f"파싱 에러: {e}")

        stmt_type = parsed[0].get_type() or "UNKNOWN"

        if stmt_type not in ALLOWED_STATEMENTS:
            self._log_blocked(sql, f"허용되지 않은 문 타입: {stmt_type}")
            return SQLValidationResult(False, stmt_type, [], f"'{stmt_type}' 문은 허용되지 않습니다.")

        sql_upper = sql.upper()
        found_blocked = []
        for keyword in BLOCKED_KEYWORDS:
            pattern = rf'\b{re.escape(keyword)}\b'
            if re.search(pattern, sql_upper):
                found_blocked.append(keyword)

        if found_blocked:
            self._log_blocked(sql, f"차단 키워드: {found_blocked}")
            return SQLValidationResult(False, stmt_type, found_blocked, f"위험 키워드 감지: {', '.join(found_blocked)}")

        if re.search(r'(/\*|\*/|--)', sql):
            self._log_blocked(sql, "SQL 주석 감지")
            return SQLValidationResult(False, stmt_type, [], "SQL 주석은 허용되지 않습니다.")

        return SQLValidationResult(True, stmt_type, [])

    def _log_blocked(self, sql: str, reason: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] BLOCKED: {reason}\nSQL: {sql[:200]}...\n{'='*60}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except:
            pass


def validate_sql(sql: str) -> SQLValidationResult:
    return SQLValidator().validate(sql)
```

#### 12.4 성공 기준

- [ ] SELECT 문만 통과
- [ ] DROP, DELETE, INSERT 등 100% 차단
- [ ] SQL 주석 차단
- [ ] 차단 로그 기록

---

### Step 13: Guardrails + PII 마스킹 (Task 4)

#### 13.1 학습 목표
- 정규식 패턴 매칭
- PII 탐지 및 마스킹
- 프롬프트 인젝션 방어

#### 13.2 신규 파일

| 파일 | 설명 |
|------|------|
| `core/security/__init__.py` | 패키지 초기화 |
| `core/security/pii_masker.py` | PII 마스킹 로직 |
| `core/security/guardrails.py` | 입력 검증 로직 |

#### 13.3 PII Masker 구현

```python
# core/security/pii_masker.py

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PIIPattern:
    name: str
    pattern: str
    mask: str


PII_PATTERNS = [
    PIIPattern("email", r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "***@***.***"),
    PIIPattern("phone", r'\b(010|011|016|017|018|019)[-.\\s]?\\d{3,4}[-.\\s]?\\d{4}\b', "***-****-****"),
    PIIPattern("ssn", r'\b\\d{6}[-.\\s]?[1-4]\\d{6}\b', "******-*******"),
    PIIPattern("credit_card", r'\b\\d{4}[-.\\s]?\\d{4}[-.\\s]?\\d{4}[-.\\s]?\\d{4}\b', "****-****-****-****"),
]


class PIIMasker:
    def __init__(self, patterns: List[PIIPattern] = None):
        self.patterns = patterns or PII_PATTERNS
        self._compiled = [
            (p.name, re.compile(p.pattern, re.IGNORECASE), p.mask)
            for p in self.patterns
        ]

    def mask(self, text: str) -> Tuple[str, List[str]]:
        detected = []
        masked_text = text

        for name, pattern, mask in self._compiled:
            if pattern.search(masked_text):
                detected.append(name)
                masked_text = pattern.sub(mask, masked_text)

        return masked_text, detected


def mask_pii(text: str) -> Tuple[str, List[str]]:
    return PIIMasker().mask(text)
```

#### 13.4 성공 기준

- [ ] PII 패턴 100% 마스킹
- [ ] 프롬프트 인젝션 차단
- [ ] 정상 질문 통과

---

## 7. Phase F: UX

### Step 14: Streaming + 대화 히스토리 (Task 13)

#### 14.1 학습 목표
- Server-Sent Events (SSE) 개념
- FastAPI StreamingResponse
- 세션 기반 대화 메모리 관리

#### 14.2 신규 파일

| 파일 | 설명 |
|------|------|
| `core/memory/__init__.py` | 패키지 초기화 |
| `core/memory/conversation.py` | 대화 히스토리 관리 |

#### 14.3 대화 히스토리 구현

```python
# core/memory/conversation.py

from typing import List, Dict
from collections import deque
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class ConversationMemory:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history: deque = deque(maxlen=max_turns * 2)

    def add_user_message(self, content: str):
        self.history.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.history.append(AIMessage(content=content))

    def get_messages(self) -> List[BaseMessage]:
        return list(self.history)

    def clear(self):
        self.history.clear()


_sessions: Dict[str, ConversationMemory] = {}


def get_memory(session_id: str) -> ConversationMemory:
    if session_id not in _sessions:
        _sessions[session_id] = ConversationMemory()
    return _sessions[session_id]


def clear_memory(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
```

#### 14.4 성공 기준

- [ ] 첫 토큰 출력 시간 <= 1초
- [ ] 실시간 타이핑 효과 표시
- [ ] 세션별 대화 히스토리 유지

---

## 8. 부록

### A. 전체 신규 의존성

```txt
# requirements.txt에 추가

# Phase 2 - 평가
ragas>=0.2.0
datasets>=2.0.0

# Phase 2 - 모니터링
langsmith>=0.1.0

# Phase 2 - 보안
sqlparse>=0.5.0

# Phase 2 - 검색 고도화
rank-bm25>=0.2.0               # FAISS 실험용 BM25
opensearch-py>=2.4.0            # OpenSearch 클라이언트 (프로덕션 hybrid search)
sentence-transformers>=3.0.0

# Phase 2 - UX
sse-starlette>=1.0.0
sseclient-py>=1.0.0
```

### B. 환경 변수 템플릿

```bash
# .env 파일에 추가

# === Phase 2 설정 ===

# LangSmith 트레이싱
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=enterprise-hr-agent
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# Guardrails
GUARDRAILS_ENABLED=true

# OpenSearch (Hybrid Search - 프로덕션)
OPENSEARCH_URL=http://localhost:9200
RAG_RETRIEVER_TYPE=faiss  # faiss (기본값) 또는 opensearch

# Hybrid Search (FAISS 실험용, OpenSearch 마이그레이션 후 불필요)
USE_HYBRID_SEARCH=true
BM25_WEIGHT=0.5
FAISS_WEIGHT=0.5

# Re-ranking
USE_RERANKING=true
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-12-v2

# SQL 고도화
USE_SCHEMA_ENHANCEMENT=true
USE_FEWSHOT=true
USE_MASKED_FEWSHOT=false
USE_COT=true
```

### C. 신규 디렉토리 구조

```
core/
├── security/          # Phase 2: 보안
│   ├── __init__.py
│   ├── pii_masker.py
│   ├── guardrails.py
│   └── sql_validator.py
│
├── retrieval/         # Phase 2: OpenSearch 검색 ★신규
│   ├── __init__.py
│   ├── korean_bm25.py           # 기존 Kiwi BM25
│   └── opensearch_retriever.py  # OpenSearch hybrid retriever
│
├── search/            # Phase 2: FAISS 검색 (실험용, 레거시)
│   ├── __init__.py
│   ├── bm25_retriever.py
│   ├── hybrid_retriever.py
│   └── reranker.py
│
├── sql/               # Phase 2: SQL 고도화 ★신규
│   ├── __init__.py
│   ├── fewshot_index.py
│   └── masked_fewshot.py
│
└── memory/            # Phase 2: 대화 히스토리
    ├── __init__.py
    └── conversation.py

data/
├── schema_metadata.json       # Phase 2: 스키마 설명 ★신규
└── fewshot/                   # Phase 2: Few-shot 인덱스 ★신규
    ├── sql_examples.faiss
    └── sql_masked_examples.faiss

notebooks/phase2/
├── study/                     # 학습 노트북
│   ├── study_01_langsmith.ipynb
│   ├── study_02_sql_evaluation.ipynb
│   ├── ...
│   └── study_14_streaming.ipynb
├── step_01_langsmith.ipynb    # 구현 노트북
├── step_02_sql_evaluation.ipynb
├── ...
├── step_14_streaming.ipynb
└── step_15_final_evaluation.ipynb
```

### D. 노트북 매핑

| Step | Task | 학습 노트북 | 구현 노트북 | 내용 |
|------|------|-------------|-------------|------|
| 1 | Task 3 | study_01_langsmith | step_01_langsmith | LangSmith 트레이싱 |
| 2 | Task 2 | study_02_sql_evaluation | step_02_sql_evaluation | SQL 평가 버그 수정 |
| 3 | Task 1 | study_03_rag_evaluation | step_03_rag_evaluation | RAGAS 평가 |
| 4 | Task 7 | study_04_chunking | step_04_chunking | 청킹 최적화 |
| 5 | Task 9 | study_05_hybrid_search | step_05_hybrid_search | Hybrid Search (BM25+FAISS) |
| 5.5 | Task 9 | - | step_06_opensearch_hybrid | OpenSearch Hybrid 실험/평가 비교 |
| 6 | Task 8 | study_06_reranker | step_07_reranker | Reranker |
| 7 | Task 11 | study_07_schema_enhancement | step_07_schema_enhancement | 스키마 설명 추가 |
| 8 | Task 10 | study_08_fewshot_embedding | step_08_fewshot_embedding | Few-shot 임베딩 검색 |
| 9 | Task 10-2 | study_09_masked_fewshot | step_09_masked_fewshot | 마스크 질문 임베딩 |
| 10 | Task 10-3 | study_10_cot_prompting | step_10_cot_prompting | CoT 프롬프팅 |
| 11 | Task 12 | study_11_sqlcoder | step_11_sqlcoder_comparison | SQLCoder 비교 (선택적) |
| 12 | Task 5 | study_12_sql_validation | step_12_sql_validation | SQL 쿼리 검증 |
| 13 | Task 4 | study_13_guardrails | step_13_guardrails | Guardrails + PII |
| 14 | Task 13 | study_14_streaming | step_14_streaming | Streaming + 히스토리 |
| 15 | - | - | step_15_final_evaluation | 최종 평가 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-12 | 초안 작성 |
| 2.0 | 2025-01-16 | **2025 현업 표준 적용**: Phase A-F 순서 재정렬, SQL 고도화(Step 4-8) 추가, RAG 순서 수정(Hybrid→Reranker), study/ 노트북 구조 반영 |
| 2.1 | 2025-01-16 | **실행 순서 변경**: RAG 먼저 (Phase C, Step 4-6), SQL 나중 (Phase D, Step 7-11) - RAG는 빠르게 완료, SQL은 차별화 포인트 |
| 2.2 | 2025-02-21 | **OpenSearch 마이그레이션**: Step 10.5 (OpenSearch 실험/평가 노트북), Step 10.6 (프로덕션 마이그레이션) 추가. opensearch-py, OPENSEARCH_URL, RAG_RETRIEVER_TYPE 환경변수 추가. core/retrieval/opensearch_retriever.py, scripts/build_opensearch_index.py 신규 파일 추가 |
