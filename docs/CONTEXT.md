# 프로젝트 컨텍스트 (AI & 개발자용)

> **이 문서는:** 현재 진행 상황, 개발 방법론, 다음 작업을 담은 인수인계 문서입니다.  
> **대상:** 사람 개발자 + AI 도구 (Cursor, Copilot 등)

---

## 📋 전체 프로젝트 개요
**HR 도메인 AI Agent (16시간 포트폴리오)**
- SQL Agent: 자연어 → SQL 생성 → 실행 → Self-Correction
- RAG Agent: 사규 PDF 검색
- Router: 질문 의도 분류 후 Agent 선택
- FastAPI: REST API 제공

---

## ✅ 완료된 작업

### Phase 1: 환경 세팅 (0-2h) ✅ 100% 완료
- [x] Docker MySQL 실행
- [x] Python 환경 (3.13)
- [x] requirements.txt
- [x] 프로젝트 구조
- [x] DB 연결 테스트
- [x] `core/db_connection.py` 완성

### Phase 2: SQL Agent (2-6h) ✅ 100% 완료
**실험 파일:**
- [x] `experiments/exp_01_sql_generation.py` - 기본 SQL 생성
- [x] `experiments/exp_02_self_correction.py` - 수동 루프 Self-Correction
- [x] `experiments/exp_03_langgraph_sql.py` - LangGraph StateGraph 구현 (9개 셀)
- [x] `experiments/exp_04_sql_agent_test.py` - 리팩토링 후 테스트 (7개 셀)

**프로덕션 코드:**
- [x] `core/sql_agent.py` - SQLAgent 클래스 완성
  - `query()` 메서드로 간단 사용
  - Self-Correction (최대 3회)
  - LangGraph 기반 선언적 플로우
  - 테스트 완료 (실행 가능)

**주요 성과:**
- ✅ 자연어 → SQL 변환
- ✅ Self-Correction 작동 확인
- ✅ 복잡한 JOIN/GROUP BY 자동 생성
- ✅ LangChain 0.3.x LCEL 스타일 적용

---

### Phase 3: RAG Agent (6-9h) ✅ 100% 완료
**실험 파일:**
- [x] `experiments/exp_05_document_loading.py` - PDF/TXT 로드 + 청킹
- [x] `experiments/exp_06_faiss_index.py` - FAISS 인덱스 생성 및 검색
- [x] `experiments/exp_07_rag_chain.py` - RAG Chain 구현
- [x] `experiments/exp_08_rag_agent_test.py` - 리팩토링 후 테스트

**프로덕션 코드:**
- [x] `core/rag_agent.py` - RAGAgent 클래스 완성
  - `query()` 메서드로 간단 사용
  - FAISS 기반 벡터 검색
  - OpenAI Embeddings (text-embedding-3-small)
  - LangChain LCEL 스타일 RAG Chain
  - 테스트 완료 (실행 가능)

**데이터:**
- [x] `data/company_docs/회사규정.txt` - 샘플 규정 문서
- [x] `data/company_docs/회사규정.pdf` - PDF 버전
- [x] `data/faiss_index/` - FAISS 인덱스 저장 완료

**주요 성과:**
- ✅ PDF/TXT 문서 로드 및 청킹
- ✅ FAISS 벡터 검색 작동 확인
- ✅ RAG Chain 답변 생성
- ✅ 규정 기반 정확한 답변 제공

---

### Phase 4: Router + 통합 (9-11h) ✅ 100% 완료
**실험 파일:**
- [x] `experiments/exp_09_router.py` - Router 의도 분류 실험 (6셀)
- [x] `experiments/exp_10_graph.py` - LangGraph 통합 실험 (9셀)
- [x] `experiments/exp_11_integration_test.py` - 통합 테스트 (10셀)

**프로덕션 코드:**
- [x] `core/router.py` - Router 클래스 완성
  - LLM 기반 질문 의도 분류
  - SQL_AGENT / RAG_AGENT 선택
  - 안전한 폴백 메커니즘
- [x] `core/graph.py` - HRAgent 클래스 완성
  - LangGraph StateGraph 기반
  - Router → SQL/RAG Agent 통합
  - `query()` 메서드로 간단 사용
  - verbose 모드 지원

**주요 성과:**
- ✅ 질문 의도 분류 정확도 높음
- ✅ SQL/RAG Agent 원활한 통합
- ✅ LangGraph 조건부 라우팅 작동
- ✅ 통합 테스트 성공

---

## 🚧 진행 중 / 미착수

### Phase 5: FastAPI + Docker (11-14h) ✅ 100% 완료
**FastAPI 구조 (현업 표준):**
- [x] app/ 구조 설계 (15개 파일)
  - [x] app/main.py - FastAPI 앱
  - [x] app/core/ - 설정 및 의존성
  - [x] app/models/ - Pydantic 모델
  - [x] app/services/ - 비즈니스 로직
  - [x] app/api/v1/endpoints/ - 엔드포인트
- [x] GET / - 루트 (API 정보)
- [x] GET /api/v1/health - 헬스체크
- [x] POST /api/v1/query - HR 질의 처리
- [x] CORS 설정
- [x] 로컬 실행 확인 ✅

**Docker 설정:**
- [x] Dockerfile (Python 3.11 기반)
- [x] docker-compose.yml (DB + API)
- [x] .dockerignore
- [x] Docker Compose 설정 완료
- [x] 로컬 테스트 완료

**API 테스트:**
- [x] Swagger UI 사용 가능 (/docs)
- [x] 루트/Health 엔드포인트 확인
- [x] test_api.py 스크립트 작성
- [x] SQL/RAG 질문 테스트 준비 완료

**주요 성과:**
- ✅ 현업 표준 FastAPI 구조 (15개 파일)
- ✅ 3-tier architecture 적용
- ✅ Docker 설정 완료 (Dockerfile + docker-compose.yml)
- ✅ API 문서 자동 생성 (Swagger/ReDoc)
- ✅ CORS, 의존성 주입, Pydantic 검증

### Phase 6: 마무리 (14-16h) ⏭️ 미착수
- [ ] 수동 테스트 (10개 시나리오)
- [ ] 시연 영상 촬영 (GIF)
- [ ] README 완성
- [ ] (선택) 배포

---

## 🎯 개발 방법론 (중요!)

### 1. 셀 단위 개발 (# %%)
```python
# %%
# 셀 N: 간단한 설명
코드...

# %%
```
- Jupyter 스타일 셀 구분자 사용
- 사용자가 하나씩 실행하며 학습

### 2. 셀 생성 규칙 (엄수!)
- **한 번에 셀 1개씩만 생성**
- 명령 받기 전에 절대 여러 셀 만들지 말 것
- 셀당 **평균 20줄, 최대 30줄**
- 30줄 넘을 것 같으면 **사전 보고 및 허락**

### 3. 셀 구성
```python
# %%
# 셀 N: 기능 설명
def some_function():
    """정의"""
    pass

print("✅ 함수 정의 완료")

# 테스트
result = some_function()
print(f"결과: {result}")

# %%
```
- **정의 + 테스트** 함께 포함
- 바로 실행해서 확인 가능하게

### 4. 셀 설명 필수
각 셀 생성 후:
```
셀 N: 제목

왜 만들었나?
- 이유

뭐하는 셀?
- 기능 설명

핵심:
- 한 줄 요약
```

### 5. 진행률 표시
```
진행률: N/총개수 = X%
```
- 셀 5부터 표시
- 사용자가 진행 상황 파악

### 6. 실험 → 프로덕션 분리
```
experiments/exp_XX.py  → 학습용, 셀 단위, 테스트 포함
core/xxx.py            → 프로덕션, 클래스 캡슐화, 재사용
experiments/exp_XX_test.py → 프로덕션 코드 테스트
```

### 7. 코드 스타일
- **LangChain 0.3.x LCEL** 사용 (현업 표준)
```python
# ✅ LCEL (Pipe 연산자)
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"key": "value"})

# ❌ 구버전
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(question="...")
```

---

## 📁 현재 파일 구조

```
c:\workspace\enterprise-hr-agent\
├─ core/
│  ├─ db_connection.py       ✅ DB 연결 헬퍼
│  ├─ sql_agent.py            ✅ SQL Agent 클래스
│  ├─ rag_agent.py            ✅ RAG Agent 클래스
│  ├─ router.py               ✅ Router 클래스
│  └─ graph.py                ✅ HRAgent 통합 클래스
│
├─ experiments/
│  ├─ exp_01_sql_generation.py      ✅ SQL 생성 (학습)
│  ├─ exp_02_self_correction.py     ✅ Self-Correction (학습)
│  ├─ exp_03_langgraph_sql.py       ✅ LangGraph 구현 (9셀)
│  ├─ exp_04_sql_agent_test.py      ✅ 프로덕션 테스트 (7셀)
│  ├─ exp_05_document_loading.py    ✅ 문서 로드 + 청킹 (학습)
│  ├─ exp_06_faiss_index.py         ✅ FAISS 인덱스 + 검색 (학습)
│  ├─ exp_07_rag_chain.py           ✅ RAG Chain 구현 (학습)
│  ├─ exp_08_rag_agent_test.py      ✅ 프로덕션 테스트
│  ├─ exp_09_router.py              ✅ Router 실험 (6셀)
│  ├─ exp_10_graph.py               ✅ 통합 그래프 실험 (9셀)
│  └─ exp_11_integration_test.py    ✅ 통합 테스트 (10셀)
│
├─ data/
│  ├─ db_init/init.sql        ✅ 초기 DB 스키마
│  ├─ company_docs/           ✅ 회사 규정 문서 (TXT + PDF)
│  └─ faiss_index/            ✅ FAISS 인덱스 저장 완료
│
├─ app/                       ⏭️ FastAPI 앱 (미착수)
├─ docs/
│  ├─ PLANNING.md             ✅ 원래 계획서
│  └─ CONTEXT.md              ✅ 이 문서 (인수인계)
│
├─ requirements.txt           ✅
├─ docker-compose.yml         ✅
└─ README.md                  🔄 업데이트 필요
```

---

## ⏰ 시간 현황
- **사용:** 약 14시간
- **남음:** 2시간
- **전체 진행률:** 약 95%

## 📊 Phase별 진행률
```
Phase 1: 환경 세팅        ████████████████████ 100% ✅
Phase 2: SQL Agent        ████████████████████ 100% ✅
Phase 3: RAG Agent        ████████████████████ 100% ✅
Phase 4: Router + 통합    ████████████████████ 100% ✅
Phase 5: FastAPI          ████████████████████ 100% ✅
Phase 6: 마무리           ···················· 0%   ⏭️

전체: ███████████████████· 95%
```

**Phase별 가중치:**
- Phase 1: 10% (환경 세팅)
- Phase 2: 30% (SQL Agent - 핵심)
- Phase 3: 25% (RAG Agent - 핵심)
- Phase 4: 15% (통합)
- Phase 5: 15% (API)
- Phase 6: 5% (마무리)

---

## 🎯 다음 세션 시작점

### 즉시 시작할 작업: Phase 5 (FastAPI)

**Step 1: FastAPI 서버 구축**
```
app/main.py 생성
- FastAPI 앱 초기화
- POST /query 엔드포인트
- GET /health 엔드포인트
- CORS 설정
```

**Step 2: 테스트**
```
- Postman/curl로 API 테스트
- 다양한 질문 시나리오
- 오류 처리 확인
```

**예상 작업량:**
- app/main.py 구현 (약 100-150줄)
- app/__init__.py
- 수동 테스트 (10개 시나리오)

---

## 💡 주의사항

### 절대 하지 말 것:
1. ❌ 한 번에 여러 셀 생성
2. ❌ 30줄 넘는 셀 (허락 없이)
3. ❌ 테스트 없는 코드
4. ❌ 구버전 LangChain 스타일

### 꼭 할 것:
1. ✅ 셀 하나씩
2. ✅ 정의 + 테스트
3. ✅ 셀 설명 (왜, 뭐하는지)
4. ✅ 진행률 표시 (셀 5부터)
5. ✅ LCEL 스타일 (0.3.x)

---

## 📊 기술 스택 확인

**완료:**
- ✅ Python 3.13
- ✅ LangChain 0.3.x (LCEL)
- ✅ LangGraph (StateGraph)
- ✅ OpenAI (gpt-4o-mini)
- ✅ MySQL + SQLAlchemy
- ✅ Docker
- ✅ FAISS (벡터 DB)
- ✅ OpenAI Embeddings (text-embedding-3-small)
- ✅ LangChain DocumentLoader
- ✅ RecursiveCharacterTextSplitter

**다음 필요:**
- ⏭️ FastAPI (Phase 5)
- ⏭️ Router 구현 (Phase 4)
- ⏭️ LangGraph 통합 (Phase 4)

---

## 🔥 핵심 성과물

### 1. SQLAgent 사용법
```python
from core.sql_agent import SQLAgent

agent = SQLAgent(model="gpt-4o-mini", max_attempts=3)
result = agent.query("직원 수는?")

# result = {
#     "success": True,
#     "sql": "SELECT COUNT(*) FROM employees;",
#     "results": [{"COUNT(*)": 4}],
#     "error": None,
#     "attempts": 1
# }
```

**검증 완료:**
- ✅ 간단한 쿼리 성공
- ✅ 복잡한 JOIN/GROUP BY 성공
- ✅ Self-Correction 작동 확인
- ✅ 연속 질문 안정적 처리

### 2. RAGAgent 사용법
```python
from core.rag_agent import RAGAgent

agent = RAGAgent(model="gpt-4o-mini", top_k=3)
result = agent.query("연차는 몇일인가요?")

# result = {
#     "question": "연차는 몇일인가요?",
#     "answer": "1년 이상 근속한 직원에게 15일의 연차휴가가 부여됩니다.",
#     "source_docs": [...],
#     "success": True
# }
```

**검증 완료:**
- ✅ PDF/TXT 문서 로드
- ✅ FAISS 벡터 검색 정확도
- ✅ 규정 기반 답변 생성
- ✅ 없는 내용 적절히 거절

### 3. HRAgent 통합 사용법 (핵심!)
```python
from core.graph import HRAgent

# 통합 Agent 생성
agent = HRAgent(model="gpt-4o-mini", verbose=False)

# SQL 질문
result = agent.query("직원 수는?")
# → 자동으로 SQL Agent 선택 및 실행

# RAG 질문
result = agent.query("연차 규정은?")
# → 자동으로 RAG Agent 선택 및 실행

# result = {
#     "question": str,
#     "agent_type": "SQL_AGENT" or "RAG_AGENT",
#     "final_answer": str,
#     "success": bool
# }
```

**검증 완료:**
- ✅ Router 정확한 의도 분류
- ✅ SQL/RAG Agent 원활한 통합
- ✅ LangGraph 조건부 라우팅
- ✅ 연속 질문 안정적 처리

---

## 📝 다음 세션 체크리스트

새 세션 시작 시 확인:
- [x] Phase 1 완료 ✅
- [x] Phase 2 완료 ✅
- [x] Phase 3 완료 ✅
- [x] Phase 4 완료 ✅
- [ ] Phase 5 시작: FastAPI
- [ ] app/main.py 구현
- [ ] API 테스트
- [ ] Phase 6: 마무리

**화이팅! 🚀 이제 80% 완료, API만 만들면 끝!**

