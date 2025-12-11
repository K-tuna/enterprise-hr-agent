# Troubleshooting

## 001-dotenv-로드
- 원인: dev.py에서 .env 파일 로드하지 않음
- 해결: dotenv load 추가
- 파일: `dev.py`

## 002-스키마-샘플-데이터
- 원인: 스키마에 테이블 구조만 있고 실제 데이터 없음
- 해결: 샘플 데이터 포함 (코드성 테이블 전체, 일반 테이블 3개)
- 파일: `core/database/connection.py`

## 003-부서명-한글화
- 원인: DB가 영문(Engineering)인데 사용자는 한글(개발팀)로 질문
- 해결: DB 데이터를 한글로 변경
- 파일: `data/db_init/init.sql`

## 004-attendance-더미-데이터
- 원인: attendance 테이블에 데이터 없음
- 해결: 직원별 3~4건 근태 데이터 추가
- 파일: `data/db_init/init.sql`

## 005-router-분류-오류
- 원인: 프롬프트가 키워드 나열식이라 경계 케이스 판단 못함
- 해결: 의도 기반 분류 기준 + 헷갈리는 케이스 Few-shot 추가
- 파일: `core/routing/router.py`

## 006-sql-결과-포맷팅
- 원인: if문 기반 포맷팅으로 "명/회/원" 등 단위 판단 불가
- 해결: LLM 기반 자연어 답변 생성으로 변경
- 파일: `core/agents/sql_agent.py`

## 007-enum-값-매핑
- 원인: 스키마에 ENUM 가능한 값이 없어서 LLM이 잘못된 값 사용
- 해결: 스키마 출력 시 ENUM 값 명시
- 파일: `core/database/connection.py`

## 008-RAG-재택근무-검색실패
- 원인: FAISS 인덱스가 구 PDF로 생성되어 재택근무 내용 없음
- 해결: 새 PDF(02_회사규정.pdf)로 재인덱싱
- 파일: `experiments/exp_06_faiss_index.py`, `data/faiss_index/`

## 009-docker-볼륨-초기화
- 원인: 바인드 마운트(`./data/mysql_data`)라서 `docker-compose down -v`로 안 지워짐
- 해결: 네임드 볼륨(`mysql_data`)으로 변경
- 파일: `docker-compose.yml`

## 010-빈문자열-입력처리
- 원인: 빈 문자열 입력 시 Router가 임의로 해석해서 이상한 답변
- 해결: HRAgent.query()에 빈 문자열 검증 추가
- 파일: `core/agents/hr_agent.py`

---

## 배운 점

### 환경 설정
1. 개발 스크립트에서는 **dotenv 로드** 확인 필수 (001)

### 데이터 설계
1. 사용자 질문 언어와 **DB 데이터 언어 일치** 필요 (003)
2. 더미 데이터는 **다양한 케이스**(ENUM 값 골고루) 포함해야 테스트 가능 (004)
3. 스키마에 **샘플 데이터/ENUM 값** 제공이 Text-to-SQL 정확도에 핵심 (002, 007)

### LLM 활용
1. 프롬프트는 키워드 나열보다 **의도 기반 기준**이 효과적 (005)
2. LLM에게 맥락 판단을 맡기면 **if문 지옥 탈출** 가능 (006)
3. 입력 검증은 **최소한**(빈 문자열)으로, 나머지는 LLM에게 위임 (010)

### 인프라
1. 문서 변경 시 **FAISS 인덱스 재생성** 필수 (008)
2. DB 데이터는 **네임드 볼륨** 사용 (바인드 마운트는 `down -v`로 안 지워짐) (009)
