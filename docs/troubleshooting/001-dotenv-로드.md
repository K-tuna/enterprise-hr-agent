# dev.py dotenv 로드 오류

## 문제
- `python dev.py` 실행 시 오류 발생
- `OpenAIError: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable`

## 원인
- `.env` 파일에 `OPENAI_API_KEY`가 있지만 로드하지 않음
- `dev.py`에서 `dotenv` 사용하지 않음

## 해결 과정

### 시도 1: dotenv 로드 추가
- 파일: `dev.py:1-15`
- 변경 전:
```python
import os
import sys

# 환경변수 설정
os.environ["DATABASE_URL"] = "mysql+pymysql://user:password@localhost:3306/enterprise_hr_db?charset=utf8mb4"
```
- 변경 후:
```python
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DATABASE_URL이 없으면 기본값 설정
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "mysql+pymysql://user:password@localhost:3306/enterprise_hr_db?charset=utf8mb4"
```
- 결과: 성공

## 검증
- 테스트: `python dev.py`
- 기대 결과: 오류 없이 실행
- 실제 결과: `[DEBUG] Container 초기화 완료` ✅
