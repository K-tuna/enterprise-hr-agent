# 프로젝트 로드맵

---

## Phase 진행 현황

| Phase | 내용 | 상태 |
|-------|------|------|
| 1 | 환경 세팅 (Docker, DB, 구조) | ✅ 완료 |
| 2 | SQL Agent (Self-Correction) | ✅ 완료 |
| 3 | RAG Agent (FAISS) | ✅ 완료 |
| 4 | Router + LangGraph 통합 | ✅ 완료 |
| 5 | FastAPI + Docker | ✅ 완료 |
| 6 | Streamlit UI | ✅ 완료 |
| 7 | 리팩토링 (DI Container) | ✅ 완료 |

---

## 완료된 작업

### Phase 1-5: 핵심 기능
- [x] Docker MySQL 실행
- [x] SQL Agent + Self-Correction
- [x] RAG Agent + FAISS 벡터 검색
- [x] Router (의도 분류)
- [x] LangGraph 통합 그래프
- [x] FastAPI REST API
- [x] Docker Compose 설정

### Phase 6: Streamlit UI
- [x] 채팅 UI 구현
- [x] Agent 타입 뱃지 (SQL/RAG)
- [x] docker-compose에 streamlit 서비스 추가

### Phase 7: 리팩토링
- [x] DI Container 패턴 적용
- [x] core/ 폴더 구조 개선 (agents/, database/, routing/, types/)
- [x] 에러 타입 정의 (core/types/errors.py)

---

## TODO

### 필수
- [ ] AWS EC2 배포
- [ ] README 보강

### 권장
- [ ] 아키텍처 다이어그램
- [ ] 시연 GIF

### 보너스
- [ ] 다양한 LLM 지원 (Ollama)
- [ ] GitHub Actions CI/CD
- [ ] HTTPS 설정

---

## 트러블슈팅

주요 이슈와 해결 과정은 `docs/troubleshooting/README.md` 참고.
