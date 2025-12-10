# 🤖 Enterprise HR AI Agent

<div align="center">

**자연어로 질문하면 자동으로 SQL 실행하거나 사규 검색해주는 Multi-Agent 시스템**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.27-1C3C3C?style=flat)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

[데모 보기](#-데모) · [빠른 시작](#-빠른-시작) · [API 문서](#-api-엔드포인트)

</div>

---

## 🎯 핵심 차별점

### 1. **Self-Correction SQL Agent** ⚡
잘못된 SQL이 생성되어도 에러 메시지를 분석해 **자동으로 3번까지 재시도**
```
❌ 1차 시도: SELECT * FROM employee WHERE dept = 'Sales'
   → Error: Table 'employee' doesn't exist

✅ 2차 시도: SELECT * FROM employees WHERE dept_id = (SELECT dept_id FROM departments WHERE name = 'Sales')
   → Success!
```

### 2. **Router 기반 Multi-Agent** 🔀
질문 의도를 LLM이 자동 분석하여 **적절한 Agent로 분기**
- "직원 수는?" → SQL Agent
- "연차 규정은?" → RAG Agent
- Few-shot 프롬프트로 정확한 의도 분류

### 3. **현업 표준 아키텍처** 🏗️
- **LangGraph StateGraph**: 복잡한 플로우 선언적 구현
- **FastAPI 3-tier**: API/Service/Model 분리 (15개 파일)
- **FAISS 벡터 검색**: Meta의 고성능 라이브러리
- **Docker Compose**: 원클릭 실행 환경

---

## 🏛️ 아키텍처

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │ 자연어 질문
       ▼
┌───────────────────────────────────────────┐
│         FastAPI Server                    │
│  ┌──────────────────────────────────┐    │
│  │     HRAgent (LangGraph)          │    │
│  │                                  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │   Router (LLM)            │  │    │
│  │  │  "SQL or RAG?"            │  │    │
│  │  └───────────┬───────────────┘  │    │
│  │              │                   │    │
│  │        ┌─────┴─────┐            │    │
│  │        ▼           ▼            │    │
│  │   ┌────────┐  ┌──────────┐     │    │
│  │   │  SQL   │  │   RAG    │     │    │
│  │   │ Agent  │  │  Agent   │     │    │
│  │   └────┬───┘  └────┬─────┘     │    │
│  │        │           │            │    │
│  │        │      ┌────┴─────┐     │    │
│  │        │      │  FAISS   │     │    │
│  │        │      │  Index   │     │    │
│  │        │      └──────────┘     │    │
│  └────────┼───────────────────────┘    │
│           │                             │
└───────────┼─────────────────────────────┘
            │
            ▼
       ┌─────────┐
       │  MySQL  │
       │   DB    │
       └─────────┘
     (Docker Container)
```

---

## 🛠️ 기술 스택

| 카테고리 | 기술 | 선택 이유 |
|---------|------|----------|
| **LLM Framework** | LangChain 0.3.27 | LTS 지원 (2026.12까지), LCEL 스타일 |
| **Graph Engine** | LangGraph 0.2.60 | Self-Correction 루프 구현 필수 |
| **LLM** | OpenAI gpt-4o-mini | 성능/비용 최적 모델 |
| **Vector DB** | FAISS 1.9.0 | Meta, 고성능 벡터 검색 |
| **Web Framework** | FastAPI 0.115 | Async, 자동 문서화, 현업 표준 |
| **Database** | MySQL 8.0 | 엔터프라이즈 HR 시스템 표준 |
| **Infra** | Docker Compose | 개발/배포 환경 일치 |

---

## 📡 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | API 정보 |
| GET | `/api/v1/health` | 헬스 체크 |
| POST | `/api/v1/query` | HR 질의 처리 (핵심!) |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc 문서 |

### POST /api/v1/query

**Request:**
```json
{
  "question": "개발팀 평균 급여는?"
}
```

**Response:**
```json
{
  "question": "개발팀 평균 급여는?",
  "answer": "7,250,000원",
  "agent_type": "SQL_AGENT",
  "success": true,
  "error": null
}
```

---

## 🎬 데모

### 📊 SQL Agent (Self-Correction)

**질문:** "영업팀 평균 급여 알려줘"

```
[1차 시도 실패]
SQL: SELECT AVG(salary) FROM employee WHERE dept = 'Sales'
Error: Table 'employee' doesn't exist

[2차 시도 성공] ✅
SQL: SELECT AVG(s.base_salary) 
     FROM salaries s 
     JOIN employees e ON s.emp_id = e.emp_id 
     JOIN departments d ON e.dept_id = d.dept_id 
     WHERE d.name = 'Sales'
     
Result: 6,500,000원
```

### 📚 RAG Agent (FAISS 검색)

**질문:** "육아휴직은 몇 개월까지 가능해?"

```
[FAISS 검색]
Top 3 유사 문서 검색 → 규정 2.4 "출산/육아휴직" 발견

[LLM 답변 생성]
"육아휴직은 최대 1년(12개월)까지 가능하며, 
통상임금의 80%가 지급됩니다."

[참조 문서]
- 회사규정.pdf, 2.4절
```

### 🔀 Router (자동 분기)

| 질문 | 분류 결과 |
|------|----------|
| "김철수 연봉은?" | SQL_AGENT ✅ |
| "재택근무 규정은?" | RAG_AGENT ✅ |
| "부서별 직원 수는?" | SQL_AGENT ✅ |
| "복지 제도 알려줘" | RAG_AGENT ✅ |

Few-shot 프롬프트로 정확한 의도 분류

---

## 📁 프로젝트 구조

```
enterprise-hr-agent/
├── app/                          # FastAPI 애플리케이션 (현업 구조)
│   ├── main.py                  # 앱 진입점
│   ├── core/                    # 설정 & 의존성
│   ├── models/                  # Pydantic 모델
│   ├── services/                # 비즈니스 로직
│   └── api/v1/endpoints/        # API 엔드포인트
│
├── core/                         # Agent 구현 (프로덕션)
│   ├── sql_agent.py             # SQL Agent + Self-Correction
│   ├── rag_agent.py             # RAG Agent (FAISS)
│   ├── router.py                # 의도 분류기
│   └── graph.py                 # LangGraph 통합
│
├── experiments/                  # 개발 과정 (학습용, 11개 파일)
│   ├── exp_01_sql_generation.py
│   ├── exp_03_langgraph_sql.py
│   ├── exp_06_faiss_index.py
│   └── ...
│
├── data/
│   ├── db_init/init.sql         # MySQL 스키마 + 더미 데이터
│   ├── company_docs/            # 사규 문서 (PDF/TXT)
│   └── faiss_index/             # 벡터 인덱스
│
├── Dockerfile                    # Python 3.11 기반
├── docker-compose.yml           # DB + API 통합
└── requirements.txt             # 의존성 (LangChain, FastAPI 등)
```

---

## 🔬 기술적 하이라이트

### 1. Self-Correction with LangGraph
```python
# 전통적인 방법 (단순 루프)
for attempt in range(3):
    sql = generate_sql(question)
    result, error = execute_sql(sql)
    if not error:
        break

# LangGraph 방식 (선언적)
workflow.add_conditional_edges(
    "execute",
    check_error,
    {
        "retry": "generate",  # 에러 시 재생성
        "end": END            # 성공 시 종료
    }
)
```

### 2. LCEL 스타일 (LangChain 0.3.x)
```python
# 체인 구성
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt 
    | llm 
    | StrOutputParser()
)

# 실행
result = chain.invoke("연차는 몇일?")
```

### 3. Few-shot 프롬프트 (Router)
```python
template = """
<분류 예시>
질문: "직원은 총 몇 명인가요?" → SQL_AGENT
질문: "연차 규정 알려줘" → RAG_AGENT
질문: "개발팀 평균 급여는?" → SQL_AGENT
...

질문: {question}
분류:"""
```

---


## 🎯 핵심 기능 상세

### SQL Agent
- ✅ 자연어 → SQL 자동 생성
- ✅ 스키마 자동 인식
- ✅ Self-Correction (최대 3회)
- ✅ 복잡한 JOIN/GROUP BY 지원
- ✅ 에러 메시지 기반 수정

### RAG Agent
- ✅ PDF/TXT 문서 로드
- ✅ RecursiveCharacterTextSplitter (청킹)
- ✅ OpenAI Embeddings (text-embedding-3-small)
- ✅ FAISS 벡터 검색 (Top-K=3)
- ✅ 참조 문서 출처 제공

### Router
- ✅ LLM 기반 의도 분류
- ✅ Few-shot 프롬프트 (8개 예시)
- ✅ 안전한 폴백 (불확실 시 RAG)

---

## 💡 확장 가능성

이 프로젝트는 **프로덕션 레벨의 기반**을 갖추고 있어, 다양한 방향으로 확장 가능합니다:

**Agent 확장**
- Tool Agent: 외부 API 연동 (Slack, Jira 등)
- Vision Agent: 문서 이미지 분석
- Memory Agent: 장기 대화 컨텍스트

**성능 최적화**
- Query Expansion으로 RAG 정확도 향상
- Hybrid Search (BM25 + Vector) 적용
- 캐싱 레이어 추가

**프로덕션 기능**
- SSE 스트리밍 응답
- Human-in-the-loop (위험 쿼리 승인)
- 대화 히스토리 & 세션 관리

