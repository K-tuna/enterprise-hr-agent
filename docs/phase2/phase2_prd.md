# Phase 2: 평가/모니터링/보안/고도화 PRD

> **Product Requirements Document**
> 버전: 2.2
> 작성일: 2025-01-16
> 상태: Draft (2025 현업 표준 반영, OpenSearch 하이브리드 서치)

---

## 1. 개요

### 1.1 문서 목적
Phase 2는 v1.0에서 완성된 HR Agent의 **품질 측정**, **모니터링**, **보안 강화**, **성능 개선**을 목표로 한다.

### 1.2 대상 독자
- 초보 개발자 (학습 병행)
- 학습 → 구현 → 검증 사이클로 진행

### 1.3 Phase 2 한줄 요약
> "측정할 수 없으면 개선할 수 없다" - 먼저 평가 체계를 구축하고, 모니터링으로 관찰하며, 보안을 강화하고, 품질을 높인다.

### 1.4 파인튜닝과의 관계
이미 진행된 파인튜닝(qwen3:8b → qwen3-hr)의 효과를 **현업 표준 메트릭**으로 측정한다.
```
Base 모델 (qwen3:8b) → 평가 → 점수 A
Fine-tuned 모델 (qwen3-hr) → 평가 → 점수 B
비교: B > A 면 파인튜닝 성공
```

---

## 2. 배경 및 목표

### 2.1 현재 상태 (v1.0 + 파인튜닝)
| 기능 | 상태 | 비고 |
|------|------|------|
| SQL Agent | ✅ 완료 | Text-to-SQL, Self-Correction |
| RAG Agent | ✅ 완료 | FAISS 벡터 검색 |
| Router | ✅ 완료 | LLM 의도 분류 |
| API/UI | ✅ 완료 | FastAPI + Streamlit |
| 파인튜닝 | ✅ 완료 | qwen3-hr 모델 생성 |
| 평가 체계 | ⚠️ 미구현 | 노트북 기반 구현 필요 |

### 2.2 문제점
1. **평가 표준 미달**: 현재 키워드 매칭 방식 → RAGAS 표준 필요
2. **SQL 평가 미구현**: Execution Accuracy 평가 노트북 필요
3. **디버깅 어려움**: LLM 호출 과정을 추적할 수 없음
4. **보안 취약점**: PII 노출, SQL Injection 위험
5. **검색 품질 한계**: 단순 벡터 검색만 사용

### 2.3 Phase 2 목표
| 목표 | 설명 | 측정 지표 |
|------|------|----------|
| 표준 평가 | 현업 표준 메트릭 적용 | RAGAS, Execution Accuracy |
| 파인튜닝 검증 | Base vs Fine-tuned 비교 | 성능 향상률 측정 |
| 관찰성 확보 | 모든 LLM 호출 트레이싱 | LangSmith 연동 완료 |
| 보안 강화 | PII 마스킹, 위험 쿼리 차단 | 마스킹 100%, 차단 100% |
| 검색 개선 | OpenSearch Hybrid Search + Re-ranking | Context Precision +10% |
| UX 향상 | 실시간 응답, 대화 맥락 유지 | 첫 토큰 ≤ 1초 |

---

## 3. 범위

### 3.1 포함 (In Scope)
| Epic | Task ID | 제목 | 우선순위 | 상태 |
|------|---------|------|----------|------|
| 평가 시스템 | 1 | RAG 평가 (RAGAS) | High | 신규 |
| 평가 시스템 | 2 | SQL 평가 (Execution Accuracy) | High | 신규 |
| 모니터링 | 3 | LangSmith 트레이싱 | High | 신규 |
| 보안 | 4 | Guardrails + PII 마스킹 | Medium | 신규 |
| 보안 | 5 | SQL Query Validation | Medium | 신규 |
| RAG 고도화 | 7 | Chunking 최적화 | High | 신규 (2025 표준) |
| RAG 고도화 | 8 | Reranker | High | 신규 (2025 표준) |
| RAG 고도화 | 9 | Hybrid Search (OpenSearch) | High | 신규 (2025 표준) |
| SQL 고도화 | 10 | Dynamic Few-shot | High | 신규 (2025 표준) |
| SQL 고도화 | 11 | Schema Enhancement | High | 신규 (2025 표준) |
| SQL 고도화 | 12 | SQLCoder 전용 모델 | High | 신규 (2025 표준) |
| UX 개선 | 13 | Streaming + 대화 히스토리 | Low | 신규 |

### 3.2 제외 (Out of Scope) → Phase 3
| Task ID | 제목 | 제외 이유 |
|---------|------|----------|
| 6 | Human-in-the-loop | 복잡도 높음, Task 5 의존, 초보자 학습 부담 |

### 3.3 별도 트랙 (파인튜닝)
- Task 11-20: 이미 완료 (`models/qwen3-8b.Q4_K_M.gguf` 존재)

---

## 4. 현업 표준 기반 요구사항

### Epic 1: 평가 시스템 (Task 1, 2)

#### FR-1.1: RAG 평가 - RAGAS 적용 (Task 1)

**현업 표준**: RAGAS (Retrieval Augmented Generation Assessment)
> "RAGAS is known for pioneering RAG-specific metrics that became **industry standard**"
> — [Confident AI](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-1.1.1 | RAGAS 라이브러리 설치 | `pip install ragas` |
| FR-1.1.2 | 기존 평가 데이터셋 변환 | `data/finetuning/rag_test.json` → RAGAS 형식 |
| FR-1.1.3 | **Faithfulness** 측정 | 답변이 컨텍스트에서 나온 것인지 (hallucination 체크) |
| FR-1.1.4 | **Answer Relevancy** 측정 | 답변이 질문에 관련있는지 |
| FR-1.1.5 | **Context Precision** 측정 | 검색된 문서 중 관련 있는 비율 |
| FR-1.1.6 | **Context Recall** 측정 | 필요한 정보가 모두 검색됐는지 |
| FR-1.1.7 | Base vs Fine-tuned 비교 | qwen3:8b vs qwen3-hr 점수 비교 |

**RAGAS 메트릭 (현업 표준):**
```python
from ragas.metrics import (
    Faithfulness,      # hallucination 체크
    AnswerRelevancy,   # 답변 관련성
    ContextPrecision,  # 검색 정확도
    ContextRecall      # 검색 재현율
)
```

**기존 방식 vs 표준 비교:**
| 기존 (비표준) | RAGAS (표준) |
|--------------|-------------|
| 키워드 매칭 | Faithfulness |
| LLM-as-Judge (1-5점) | Answer Relevancy |
| 없음 | Context Precision |
| 없음 | Context Recall |

---

#### FR-1.2: SQL 평가 - Execution Accuracy (Task 2)

**현업 표준**: Execution Accuracy
> "SQL을 실행해서 결과가 같으면 정답" - 별도 라이브러리 없이 직접 구현
> — [Defog SQL-Eval](https://github.com/defog-ai/sql-eval)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-1.2.1 | 평가 함수 구현 | 정답 SQL vs 생성 SQL 결과 비교 |
| FR-1.2.2 | Execution Accuracy 계산 | 결과 일치 비율 측정 |
| FR-1.2.3 | Exact Match 계산 (선택) | SQL 문법 일치 비율 |
| FR-1.2.4 | Base vs Fine-tuned 비교 | qwen3:8b vs qwen3-hr |
| FR-1.2.5 | 결과 저장 | JSON 파일로 저장 |

**평가 로직:**
```python
def evaluate_sql(question, gold_sql, generated_sql, db):
    """Execution Accuracy 평가"""
    try:
        gold_result = db.execute(gold_sql)
        gen_result = db.execute(generated_sql)
        is_correct = gold_result == gen_result
        return {"execution_accuracy": is_correct}
    except Exception as e:
        return {"execution_accuracy": False, "error": str(e)}
```

**RAG vs SQL 평가 비교:**
| | RAG | SQL |
|--|-----|-----|
| 표준 도구 | RAGAS 라이브러리 | 직접 구현 (DB 실행) |
| 평가 방식 | LLM-as-Judge | 결과 비교 |
| 메트릭 | Faithfulness, Relevancy | Execution Accuracy |

---

### Epic 2: 모니터링 (Task 3)

#### FR-2.1: LangSmith 트레이싱 (Task 3)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-2.1.1 | LangSmith 계정 및 API 키 설정 | 환경 변수 설정 완료 |
| FR-2.1.2 | 트레이싱 활성화 | 모든 Agent 호출이 LangSmith에 기록 |
| FR-2.1.3 | 메타데이터 태깅 | agent_type, session_id 포함 |
| FR-2.1.4 | 에러 자동 로깅 | 예외 발생 시 스택 트레이스 포함 |
| FR-2.1.5 | 대시보드 메트릭 확인 | 평균 응답 시간, 에러율 모니터링 |

**환경 변수:**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=enterprise-hr-agent
```

---

### Epic 3: 보안 (Task 4, 5)

#### FR-3.1: Guardrails + PII 마스킹 (Task 4)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-3.1.1 | PII 패턴 탐지 | 이메일, 전화번호, 주민번호 |
| FR-3.1.2 | PII 마스킹 처리 | `***@***.***`, `***-****-****` |
| FR-3.1.3 | 욕설/부적절 표현 필터 | 금지어 사전 기반 차단 |
| FR-3.1.4 | 프롬프트 인젝션 방어 | 위험 패턴 탐지 및 경고 |
| FR-3.1.5 | 미들웨어 통합 | 요청/응답 전후처리 |

#### FR-3.2: SQL Query Validation (Task 5)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-3.2.1 | SQL 문법 검증 | `sqlparse` 활용 |
| FR-3.2.2 | SELECT 문만 허용 | 화이트리스트 방식 |
| FR-3.2.3 | 위험 키워드 차단 | DROP, DELETE, INSERT, UPDATE 등 |
| FR-3.2.4 | 차단 로깅 | `logs/blocked_queries.log` 기록 |
| FR-3.2.5 | 에러 메시지 반환 | 명확한 차단 사유 제공 |

---

### Epic 4: RAG 고도화 (Task 7, 8, 9) - 2025 SOTA

**SOTA 파이프라인 순서:**
```
Chunking 최적화 → Hybrid Search (후보 수집) → Reranker (최종 정렬)
```

> **참고**: Hybrid Search로 recall 확보 후, Reranker로 precision 확보. 순서가 중요!
> — [Superlinked VectorHub](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)

#### FR-4.1: Chunking 최적화 (Task 7) - 신규

**현업 표준**: 200-300 단어 크기의 청크 + 오버랩
> "Optimal chunk size is 200-300 words with 10-20% overlap"
> — [kapa.ai RAG Lessons](https://www.kapa.ai/blog/rag-best-practices)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-4.1.1 | 현재 청킹 방식 분석 | 기존 청크 크기 확인 |
| FR-4.1.2 | 청크 크기 최적화 | 200-300 단어로 조정 |
| FR-4.1.3 | 오버랩 설정 | 10-20% 오버랩 적용 |
| FR-4.1.4 | 문서 재인덱싱 | FAISS 인덱스 재생성 |
| FR-4.1.5 | RAGAS로 효과 측정 | Context Precision 향상 확인 |

**구현 예시:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # ~200-300 단어
    chunk_overlap=50,    # 10% 오버랩
    separators=["\n\n", "\n", ".", " "]
)
```

#### FR-4.2: Reranker (Task 8) - 2025 표준

**현업 표준**: Cross-encoder 기반 Reranker
> "Adding a reranker improves RAG accuracy by 42%"
> — [RAG Best Practices 2025](https://orkes.io/blog/rag-best-practices/)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-4.2.1 | Cross-encoder 모델 설치 | `sentence-transformers` |
| FR-4.2.2 | Reranker 파이프라인 구현 | 검색 → Rerank → 결과 |
| FR-4.2.3 | Top-10 → Top-3 재정렬 | 품질 향상 |
| FR-4.2.4 | 응답 시간 측정 | 추가 지연 최소화 |
| FR-4.2.5 | RAGAS로 효과 측정 | Faithfulness 향상 확인 |

**구현 예시:**
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 검색 후 rerank
docs = retriever.get_relevant_documents(query)
pairs = [(query, doc.page_content) for doc in docs]
scores = reranker.predict(pairs)
reranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)[:3]
```

#### FR-4.3: Hybrid Search (Task 9) - OpenSearch 네이티브

**현업 표준**: OpenSearch 네이티브 hybrid query (BM25 + kNN)
> OpenSearch는 DB-Engines 벡터 DBMS 랭킹 2위 (점수 20.04)로, 네이티브 하이브리드 서치를 지원
> — [OpenSearch Hybrid Search](https://opensearch.org/docs/latest/search-plugins/hybrid-search/)

**기존 접근 (BM25+FAISS EnsembleRetriever) 대비 장점:**
| 항목 | BM25+FAISS (기존) | OpenSearch (신규) |
|------|-------------------|-------------------|
| BM25 | rank_bm25 직접 구현 | 내장 (Nori 한국어 분석기) |
| 점수 융합 | 수동 RRF/가중치 구현 | search pipeline 내장 |
| 메타데이터 필터링 | 수동 구현 | 쿼리 DSL 내장 |
| 인덱스 관리 | FAISS 파일 직접 관리 | REST API + 자동 관리 |
| 프로덕션 운영 | 제한적 | 클러스터링, 모니터링 내장 |

**현재 지표 (step_05 노트북 기준):**
| Retriever | Precision | Recall | Average |
|-----------|-----------|--------|---------|
| FAISS only | 0.8348 | 0.9500 | 0.8924 |
| BM25+FAISS (50/50) | 0.8785 | 0.9800 | 0.9292 |
| OpenSearch Hybrid | TBD | TBD | TBD |

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-4.3.1 | OpenSearch Docker 환경 구성 | `opensearchproject/opensearch:2.18.0` + Nori 한국어 분석기 |
| FR-4.3.2 | OpenSearch 인덱스 생성 | `hr_documents` 인덱스 (Nori analyzer + knn_vector 1024d) |
| FR-4.3.3 | Search Pipeline 구성 | `normalization-processor`로 BM25/kNN 점수 정규화 |
| FR-4.3.4 | Hybrid Query 구현 | BM25 match + kNN 동시 실행, 가중치 조절 가능 |
| FR-4.3.5 | RAGAS 평가 비교 | FAISS vs OpenSearch Hybrid 지표 비교 (Jupyter 노트북) |
| FR-4.3.6 | 프로덕션 마이그레이션 | 평가 결과 확인 후 RAG Agent retriever 교체 |

**OpenSearch 인덱스 매핑:**
```json
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "nori_analyzer"
      },
      "content_embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "lucene"
        }
      },
      "metadata": {
        "properties": {
          "source": { "type": "keyword" },
          "page": { "type": "integer" },
          "chunk_id": { "type": "keyword" }
        }
      }
    }
  }
}
```

**Hybrid Query 예시:**
```json
{
  "query": {
    "hybrid": {
      "queries": [
        { "match": { "content": { "query": "연차 신청 방법" } } },
        { "knn": { "content_embedding": { "vector": [...], "k": 10 } } }
      ]
    }
  },
  "search_pipeline": "hr-hybrid-pipeline"
}
```

---

### Epic 5: UX 개선 (Task 9)

#### FR-5.1: Streaming + 대화 히스토리 (Task 9)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-5.1.1 | SSE 엔드포인트 추가 | `/api/v1/query/stream` |
| FR-5.1.2 | Streamlit 실시간 표시 | 타이핑 효과 (커서 포함) |
| FR-5.1.3 | ConversationBufferMemory | 대화 맥락 유지 |
| FR-5.1.4 | 세션 관리 | 세션별 메모리 분리 |
| FR-5.1.5 | Multi-turn 대화 | 대명사 해석 ("그", "그것" 등) |

---

### Epic 6: SQL Agent 고도화 (Task 10, 10-2, 10-3, 11, 12) - 2025 SOTA

**SOTA 파이프라인 순서:**
```
Schema Enhancement → Few-shot 임베딩 → 마스크 질문 임베딩 → CoT 프롬프팅 → (선택) 전용 모델
```

> **참고**: Schema Linking 오류가 전체 오류의 27%를 차지하므로 Schema를 먼저 개선.
> — [Spider 2.0 Benchmark](https://spider2-sql.github.io/)

#### FR-6.1: Dynamic Few-shot (Task 10)

**현업 표준**: Dynamic Few-shot (RAG 방식으로 유사 예시 검색)
> "Dynamic few-shot selection using semantic similarity achieves +19% improvement over static examples"
> — [OpenSearch-SQL (2025)](https://arxiv.org/html/2502.14913v1)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-6.1.1 | 질문-SQL 예시 데이터셋 구축 | 기존 `data/finetuning/sql_training.json` 활용 |
| FR-6.1.2 | 예시 임베딩 및 FAISS 인덱스 | 질문 텍스트 임베딩 |
| FR-6.1.3 | 유사 예시 검색 | 코사인 유사도 기반 Top-3 |
| FR-6.1.4 | 프롬프트에 동적 예시 삽입 | Few-shot 프롬프트 템플릿 |
| FR-6.1.5 | 정확도 측정 | Before/After 비교 |

**구현 예시:**
```python
# 유사 질문 검색 후 프롬프트에 추가
similar_examples = faiss_index.search(query_embedding, k=3)
prompt = f"""
다음은 유사한 질문과 SQL 예시입니다:
{format_examples(similar_examples)}

질문: {user_question}
SQL:
"""
```

#### FR-6.2: Schema Enhancement (Task 11)

**현업 표준**: 스키마에 컬럼 설명 및 관계 정보 추가
> "Adding column descriptions improves accuracy by 3-5%"
> — [Schema-Aware Text-to-SQL](https://arxiv.org/abs/2402.01517)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-6.2.1 | 컬럼별 한글 설명 추가 | `employees.name` → "직원 이름" |
| FR-6.2.2 | FK 관계 명시 | `employees.dept_id → departments.dept_id` |
| FR-6.2.3 | 스키마 메타데이터 파일 | `data/schema_metadata.json` |
| FR-6.2.4 | 프롬프트에 스키마 설명 포함 | 자동 삽입 |

**스키마 메타데이터 예시:**
```json
{
  "employees": {
    "columns": {
      "emp_id": "직원 고유 ID",
      "name": "직원 이름",
      "dept_id": "소속 부서 ID (departments.dept_id 참조)"
    }
  }
}
```

#### FR-6.3: 마스크 질문 임베딩 (Task 10-2) - 신규

**SOTA 기법**: 테이블명/컬럼명을 마스킹하여 구조적 유사도 검색
> "Mask question similarity improves few-shot selection for structurally similar queries"
> — [OpenSearch-SQL (2025)](https://arxiv.org/html/2502.14913v1)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-6.3.1 | 스키마 용어 추출 | 테이블명, 컬럼명, 값 목록 |
| FR-6.3.2 | 마스킹 함수 구현 | `"개발팀 급여"` → `"[MASK] [MASK]"` |
| FR-6.3.3 | 마스크된 질문 임베딩 | FAISS 인덱스 별도 생성 |
| FR-6.3.4 | 유사 패턴 검색 | 구조적으로 유사한 쿼리 매칭 |
| FR-6.3.5 | 정확도 비교 | 일반 임베딩 vs 마스크 임베딩 |

**구현 예시:**
```python
import re

def mask_question(question, schema_terms):
    """테이블명, 컬럼명 등을 [MASK]로 치환"""
    masked = question
    for term in schema_terms:
        masked = re.sub(term, "[MASK]", masked, flags=re.IGNORECASE)
    return masked

# 사용 예시
schema_terms = ["개발팀", "영업팀", "급여", "연봉", "직원"]
masked = mask_question("개발팀 평균 급여는?", schema_terms)
# → "[MASK] 평균 [MASK]는?"
```

#### FR-6.4: CoT 프롬프팅 (Task 10-3) - 신규

**SOTA 기법**: Chain of Thought로 단계별 사고 유도
> "CoT prompting improves SQL generation accuracy by 10-15%"
> — [SQL-of-Thought (2025)](https://arxiv.org/pdf/2509.00581)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-6.4.1 | CoT 프롬프트 템플릿 작성 | 단계별 사고 구조 |
| FR-6.4.2 | SQL Agent 프롬프트 수정 | 기존 프롬프트에 CoT 추가 |
| FR-6.4.3 | 정확도 비교 | CoT 적용 전/후 비교 |

**CoT 프롬프트 템플릿:**
```
질문: {user_question}

단계별로 생각해보자:
1. 필요한 테이블:
2. 조인 조건:
3. 필터 조건:
4. 집계 함수:
5. 정렬/제한:

SQL:
```

#### FR-6.5: SQLCoder 전용 모델 (Task 12) - 선택적

**현업 표준**: Text-to-SQL 전용 모델 사용 (실험 후 적용 여부 결정)
> "SQLCoder-8B outperforms GPT-4 on SQL generation tasks"
> — [Defog SQLCoder](https://github.com/defog-ai/sqlcoder)

| ID | 요구사항 | 수용 기준 |
|----|----------|----------|
| FR-6.5.1 | SQLCoder 모델 설치 | `ollama pull mannix/defog-llama3-sqlcoder-8b` |
| FR-6.5.2 | 프롬프트 형식 변경 | SQLCoder 전용 템플릿 |
| FR-6.5.3 | 모델 전환 설정 | 환경 변수로 선택 가능 |
| FR-6.5.4 | 정확도 비교 | qwen3-hr vs SQLCoder |
| FR-6.5.5 | 적용 여부 결정 | 실험 결과 기반 |

**SQLCoder 프롬프트 형식:**
```
### Task
Generate a SQL query to answer [QUESTION]{user_question}[/QUESTION]

### Database Schema
{schema}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{user_question}[/QUESTION]
[SQL]
```

---

## 5. 실행 순서 및 의존성

### 5.1 추천 실행 순서 (2025 현업 표준 기반)

```
[Phase A] 모니터링 (Observability) - 관찰 먼저
[Step 1] Task 3: LangSmith 트레이싱 연동
         ↓

[Phase B] 평가 체계 (Measurement) - 측정할 수 있어야 개선 가능
[Step 2] Task 2: SQL 평가 (Execution Accuracy)
         ↓
[Step 3] Task 1: RAG 평가 RAGAS 적용
         ↓

[Phase C] RAG Agent 고도화 (SOTA 파이프라인 순서) - 빠르게 완료
[Step 4] Task 7: Chunking 최적화 (+10~20%)
         ↓
[Step 5] Task 9: Hybrid Search - BM25+FAISS 실험 (recall)
         ↓
[Step 5.5] Task 9: OpenSearch Hybrid 실험/평가 비교 (Jupyter)
         ↓ (OpenSearch >= FAISS 확인 후)
[Step 5.6] Task 9: OpenSearch 프로덕션 마이그레이션
         ↓
[Step 6] Task 8: Reranker (최종 정렬, precision, +42%)
         ↓

[Phase D] SQL Agent 고도화 (SOTA 파이프라인 순서) - 차별화 포인트
[Step 7] Task 11: Schema Enhancement (먼저, 오류 27% 감소)
         ↓
[Step 8] Task 10: Dynamic Few-shot 임베딩 (+19%)
         ↓
[Step 9] Task 10-2: 마스크 질문 임베딩 (SOTA)
         ↓
[Step 10] Task 10-3: CoT 프롬프팅 (+10~15%)
         ↓
[Step 11] Task 12: SQLCoder (선택적, 실험 후 결정)
         ↓

[Phase E] 보안 (Security)
[Step 12] Task 5: SQL Query Validation
         ↓
[Step 13] Task 4: Guardrails + PII 마스킹
         ↓

[Phase F] UX
[Step 14] Task 13: Streaming + 대화 히스토리
```

### 5.2 학습 → 구현 사이클 (노트북 매핑)

**폴더 구조:**
```
notebooks/phase2/
├── study/           # 학습용 노트북 (study_01 ~ study_14)
├── step_01~14.ipynb # 구현용 노트북
└── step_15.ipynb    # 최종 평가
```

**진행 방식:** `study/study_XX.ipynb` (학습) → `step_XX.ipynb` (구현) → Before/After 비교 → 적용 결정

| Step | Task | 학습 노트북 | 구현 노트북 | 내용 |
|------|------|-------------|-------------|------|
| 1 | Task 3 | study_01_langsmith | step_01_langsmith | LangSmith 트레이싱 |
| 2 | Task 2 | study_02_sql_evaluation | step_02_sql_evaluation | SQL 평가 (Execution Accuracy) |
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

## 6. 성공 지표 (KPI)

### 6.1 평가 시스템 (현업 표준 기준)

| 메트릭 | 표준 | 목표 | 측정 방법 |
|--------|------|------|----------|
| RAGAS Faithfulness | 표준 | ≥ 0.7 | `ragas.evaluate()` |
| RAGAS Answer Relevancy | 표준 | ≥ 0.7 | `ragas.evaluate()` |
| RAGAS Context Precision | 표준 | ≥ 0.7 | `ragas.evaluate()` |
| SQL Execution Accuracy | 표준 | ≥ 80% | `step_02_sql_evaluation.ipynb` |

### 6.2 Agent 고도화 효과 (2025 표준 적용 후)

| Agent | 현재 정확도 | 목표 | 주요 개선 방법 |
|-------|-------------|------|----------------|
| SQL Agent | 20~60% | 70~80% | Few-shot (+19%), SQLCoder (+10~20%) |
| RAG Agent | 0% (버그) | 60~80% | Reranker (+42%), Hybrid Search (+15%) |

### 6.3 단계별 예상 향상률

| 단계 | 적용 기술 | 예상 향상 | 누적 목표 |
|------|----------|----------|----------|
| Step 1 | Dynamic Few-shot | +19% | ~40% |
| Step 2 | Schema Enhancement | +3~5% | ~45% |
| Step 3 | SQLCoder | +10~20% | ~65% |
| Step 4 | RAG Chunking | +10~20% | - |
| Step 5 | RAG Reranker | +42% | - |
| Step 6 | Hybrid Search | +15~25% | - |

### 6.3 기타 지표

| 지표 | 목표 |
|------|------|
| PII 마스킹 성공률 | 100% |
| 위험 쿼리 차단률 | 100% |
| 평균 응답 시간 | ≤ 3초 |
| 첫 토큰 출력 시간 | ≤ 1초 |

---

## 7. 기술 스택

### 7.1 신규 라이브러리

| 라이브러리 | 버전 | 용도 | 표준 여부 |
|------------|------|------|----------|
| ragas | 0.2.x | RAG 평가 | ✅ 현업 표준 |
| opensearch-py | 2.4.x | OpenSearch 클라이언트 | ✅ 현업 표준 (DB-Engines 2위) |
| rank-bm25 | 0.2.x | BM25 검색 (FAISS 실험용) | ✅ 현업 표준 |
| sentence-transformers | 3.x | Re-ranking | ✅ 현업 표준 |
| sqlparse | 0.5.x | SQL 검증 | ✅ 현업 표준 |
| langsmith | 0.1.x | 트레이싱 | ✅ 현업 표준 |

### 7.2 환경 변수 추가

```bash
# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=enterprise-hr-agent

# Guardrails
GUARDRAILS_ENABLED=true

# OpenSearch (Hybrid Search)
OPENSEARCH_URL=http://localhost:9200
RAG_RETRIEVER_TYPE=faiss  # faiss (기본값) 또는 opensearch

# Hybrid Search (FAISS 실험용, OpenSearch 마이그레이션 후 불필요)
BM25_WEIGHT=0.5
FAISS_WEIGHT=0.5
```

### 7.3 최적 모델 구성 (8GB VRAM)

#### 아키텍처 개요

```
┌─────────────────────────────────────┐
│ 항상 로드 (상주)                     │
├─────────────────────────────────────┤
│ Qwen3-8B (4bit)     ~5GB           │ ← LLM 베이스
│ DeBERTa-v3-base     ~350MB         │ ← Router (분류)
│ BGE-small-ko        ~100MB         │ ← Embedding
├─────────────────────────────────────┤
│ 총합: ~5.5GB (여유 2.5GB)           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ LoRA 어댑터 스왑 (~45ms)            │
├─────────────────────────────────────┤
│ sql_adapter.safetensors   ~15MB    │
│ rag_adapter.safetensors   ~15MB    │
└─────────────────────────────────────┘
```

#### 모델 선정 근거

| 컴포넌트 | 모델 | 선정 이유 |
|----------|------|----------|
| **LLM 베이스** | Qwen3-8B (4bit) | Qwen3-8B ≈ Qwen2.5-14B 성능, 8GB 한계 내 최대 크기 |
| **Router** | DeBERTa-v3-base | 분류 정확도 90%+, LLM(80-85%)보다 우수 |
| **Embedding** | BGE-small-ko | 한국어 특화, 100MB로 경량 |
| **어댑터 방식** | LoRA (4bit QLoRA) | 스왑 45ms, 정확도 95-100% 유지 |

#### 워크플로우

```
질문 → DeBERTa (분류) → SQL/RAG 판단
                          ↓
         SQL → sql_adapter 로드 → Qwen3-8B 실행
         RAG → BGE 검색 → rag_adapter 로드 → Qwen3-8B 실행
```

#### 대안 비교 (기각된 옵션)

| 옵션 | 구성 | 기각 이유 |
|------|------|----------|
| 모델 스왑 | SQLCoder-7B ↔ Qwen-7B | 스왑 10-30초, 사용자 경험 저하 |
| 더 큰 모델 | Qwen3-14B | 8GB 초과 (~8GB 단독) |
| 2bit 양자화 | Qwen3-14B 2bit | 정확도 70-80%로 급락 |

#### VRAM 상세 분석

| 항목 | 크기 | 비고 |
|------|------|------|
| Qwen3-8B (4bit) | ~5GB | 베이스 모델 |
| DeBERTa-v3-base | ~350MB | Router |
| BGE-small-ko | ~100MB | Embedding |
| KV Cache | ~500MB-1GB | 추론 중 동적 할당 |
| 어댑터 | ~30MB | SQL + RAG |
| **총합** | **~6-7GB** | 8GB 내 안정 운영 |

#### 벤치마크 기반 예상 성능

| 태스크 | 예상 정확도 | 출처 |
|--------|------------|------|
| SQL (Qwen3-8B + LoRA) | ~68% | 일반 8B + LoRA 추정 |
| Router (DeBERTa) | 90%+ | GLUE 벤치마크 |
| RAG (Qwen3-8B) | 좋음 | 8B 베이스 이점 |

#### 현업 표준 대비

| 항목 | 현업 표준 | 본 구성 | 차이 |
|------|----------|--------|------|
| LLM 크기 | 70B+ | 8B | 성능 ↓, 비용 ↓↓ |
| Router | DeBERTa | DeBERTa | 동일 |
| 어댑터 스왑 | ~45ms | ~45ms | 동일 |
| Embedding | Cohere API | BGE-small-ko | 약간 ↓, 로컬 운영 |

---

## 8. 참고 자료 (현업 표준 출처)

### RAG 평가
- [RAGAS Metrics - Confident AI](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more)
- [RAG Evaluation Best Practices - Patronus AI](https://www.patronus.ai/llm-testing/rag-evaluation-metrics)
- [RAGAS 공식 문서](https://docs.ragas.io/)

### SQL 평가
- [Spider Benchmark - Yale](https://yale-lily.github.io/spider)
- [Text-to-SQL Evaluation Guide - Promethium](https://promethium.ai/guides/text-to-sql-evaluation-benchmarks-metrics/)

### SQL Agent 고도화 (2025 현업 표준)
- [OpenSearch-SQL: Dynamic Few-shot (2025)](https://arxiv.org/html/2502.14913v1)
- [Text-to-SQL without Fine-tuning (2025)](https://arxiv.org/html/2505.14174v1)
- [SQLCoder - Defog AI](https://github.com/defog-ai/sqlcoder)
- [Schema-Aware Text-to-SQL](https://arxiv.org/abs/2402.01517)

### RAG Agent 고도화 (2025 현업 표준)
- [RAG Best Practices 2025 - Orkes](https://orkes.io/blog/rag-best-practices/)
- [kapa.ai RAG Lessons](https://www.kapa.ai/blog/rag-best-practices)
- [Retriever Fine-tuning (2025)](https://arxiv.org/abs/2501.04652)
- [OpenSearch Hybrid Search](https://opensearch.org/docs/latest/search-plugins/hybrid-search/)
- [OpenSearch Nori 한국어 분석기](https://opensearch.org/docs/latest/analyzers/language-analyzers/#nori-korean)
- [DB-Engines Vector DBMS Ranking](https://db-engines.com/en/ranking/vector+dbms)

### 기타
- [LangSmith 가이드](https://docs.smith.langchain.com/)

---

## 9. 제외 항목 (Phase 3 예정)

| 항목 | 설명 | Phase 3 이유 |
|------|------|-------------|
| Human-in-the-loop | 위험 쿼리 승인 플로우 | 복잡도 높음, Redis/큐 필요 |
| Query Caching | 중복 쿼리 캐싱 | 우선순위 낮음 |
| Multi-Agent Router | 3개 이상 Agent 확장 | 현재 불필요 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-11 | 초안 작성 |
| 1.1 | 2025-01-12 | 현업 표준 반영 (RAGAS, Execution Accuracy), 파인튜닝 관계 명시, Task 2 버그 수정으로 변경 |
| 2.0 | 2025-01-15 | **2025 현업 표준 적용**: Epic 6 (SQL 고도화) 추가, Epic 4 (RAG 고도화) 순서 변경, 학습 노트북 매핑 추가 |
| 2.1 | 2025-01-16 | **실행 순서 변경**: RAG 먼저 (Phase C), SQL 나중 (Phase D) - RAG는 빠르게 완료, SQL은 차별화 포인트 |
| 2.2 | 2025-02-21 | **OpenSearch 마이그레이션**: FR-4.3을 BM25+FAISS EnsembleRetriever → OpenSearch 네이티브 hybrid query로 변경. Jupyter 노트북 실험(Phase A) → 평가 비교 → 프로덕션 마이그레이션(Phase B) 단계적 접근. opensearch-py, OPENSEARCH_URL, RAG_RETRIEVER_TYPE 추가. step_06_opensearch_hybrid 노트북 추가 |
