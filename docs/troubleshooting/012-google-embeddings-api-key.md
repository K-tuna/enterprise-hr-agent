# GoogleGenerativeAIEmbeddings API 키 오류

## 문제
- 노트북에서 Gemini 임베딩 모델 초기화 시 API 키 오류 발생
- 에러 메시지: `오류: VectorStore 생성 실패 - Error embedding content: 400 API key not valid.`
- API 키 자체는 유효함 (curl 테스트로 모델 목록 정상 반환 확인)

## 원인
- `core/llm/factory.py`에서 `GoogleGenerativeAIEmbeddings` 생성 시 `google_api_key` 파라미터 누락
- langchain-google-genai는 환경변수를 자동으로 읽지 않고 명시적으로 전달해야 함

## 해결 과정

### 시도 1: google_api_key 파라미터 추가
- 파일: `core/llm/factory.py:94-100`
- 변경 전:
```python
elif provider == "google":
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(model=model)
```
- 변경 후:
```python
elif provider == "google":
    import os
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model=model,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
```
- 결과: 성공

## 검증
```python
from core.llm.factory import create_embeddings

embeddings = create_embeddings(
    provider="google",
    model="models/text-embedding-004"
)

test_vector = embeddings.embed_query("테스트 문장")
print(f"임베딩 차원: {len(test_vector)}")  # 768
```
