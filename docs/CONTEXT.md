# 프로젝트 컨텍스트

> HR 도메인 AI Agent - 자연어로 HR 데이터 분석(SQL)과 사규 검색(RAG)을 처리

---

## 프로젝트 개요

**핵심 기능:**
- **SQL Agent**: 자연어 → SQL 생성 → 실행 → Self-Correction (최대 3회)
- **RAG Agent**: 사규 PDF/TXT 검색 (FAISS 벡터 DB)
- **Router**: 질문 의도 분류 후 Agent 선택
- **FastAPI**: REST API 제공
- **Streamlit**: 채팅 UI

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Language | Python 3.11+ |
| LLM | OpenAI gpt-4o-mini |
| Framework | LangGraph 0.2.60, LangChain 0.3.27, FastAPI 0.115.6 |
| Vector DB | FAISS (faiss-cpu) |
| Database | MySQL 8.0 (PyMySQL, SQLAlchemy) |
| Frontend | Streamlit |
| Infra | Docker Compose |

**코드 스타일:**
```python
# LangChain 0.3.x LCEL 사용
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"key": "value"})
```

---

## 아키텍처

```
[User] → [Streamlit UI] → [FastAPI]
                              ↓
                          [Router]
                         ↙      ↘
               [SQL Agent]    [RAG Agent]
                    ↓              ↓
               [MySQL]        [FAISS]
```

**DI Container 패턴:**
- `core/container.py`: 의존성 주입 컨테이너
- Settings → DatabaseConnection → Agents → HRGraph

---

## 파일 구조

```
enterprise-hr-agent/
├── core/                       # 핵심 Agent 로직
│   ├── agents/
│   │   ├── sql_agent.py        # SQL Agent (Self-Correction)
│   │   └── rag_agent.py        # RAG Agent (FAISS)
│   ├── database/
│   │   └── connection.py       # DB 연결 + 스키마 조회
│   ├── routing/
│   │   ├── router.py           # 질문 의도 분류
│   │   └── graph.py            # LangGraph 통합
│   ├── types/                  # 타입 정의
│   └── container.py            # DI Container
│
├── app/                        # FastAPI (3-tier)
│   ├── main.py
│   ├── core/                   # 설정, 의존성
│   ├── models/                 # Pydantic 모델
│   ├── services/               # 비즈니스 로직
│   └── api/v1/endpoints/       # 엔드포인트
│
├── frontend/
│   └── app.py                  # Streamlit 채팅 UI
│
├── data/
│   ├── db_init/init.sql        # DB 초기화 스크립트
│   ├── company_docs/           # 회사 규정 문서
│   └── faiss_index/            # FAISS 인덱스
│
├── experiments/                # 실험/학습용 파일
├── tests/                      # 테스트
├── docs/                       # 문서
│   ├── CONTEXT.md              # 이 문서 (프로젝트 이해)
│   ├── ROADMAP.md              # 진행 상황
│   └── troubleshooting/        # 트러블슈팅 기록
│
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 사용법

### 1. SQL Agent
```python
from core.agents.sql_agent import SQLAgent

agent = SQLAgent(model="gpt-4o-mini", max_attempts=3)
result = agent.query("개발팀 평균 급여는?")
# → SQL 자동 생성 → 실행 → 자연어 답변
```

### 2. RAG Agent
```python
from core.agents.rag_agent import RAGAgent

agent = RAGAgent(model="gpt-4o-mini", top_k=3)
result = agent.query("연차휴가 규정은?")
# → FAISS 검색 → 규정 기반 답변
```

### 3. HRGraph (통합)
```python
from core.routing.graph import HRGraph

graph = HRGraph(model="gpt-4o-mini")
result = graph.query("직원 수는?")      # → SQL Agent
result = graph.query("휴가 규정은?")    # → RAG Agent
```

### 4. API
```bash
# 실행
docker-compose up -d

# 테스트
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "직원 수는?"}'
```

### 5. Streamlit UI
```bash
streamlit run frontend/app.py
# http://localhost:8501
```

---

## DB 스키마

**주요 테이블:**
- `employees`: 직원 정보 (emp_id, name, dept_id, position, hire_date)
- `departments`: 부서 정보 (dept_id, name, location)
- `salaries`: 급여 정보 (emp_id, base_salary, bonus)
- `attendance`: 근태 기록 (emp_id, date, status, check_in, check_out)

**ENUM 값:**
- position: 사원, 대리, 과장, 부장
- status: PRESENT, LATE, VACATION, SICK_LEAVE
