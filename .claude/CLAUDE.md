# 프로젝트 규칙

## 문서 위치
- 프로젝트 컨텍스트: @docs/CONTEXT.md
- 프로젝트 로드맵: @docs/ROADMAP.md
- 트러블슈팅: @docs/troubleshooting/README.md

## 패키지 설치 규칙

**requirements.txt 변경 시 반드시 지켜야 할 규칙:**

1. **절대 `pip install` 직접 실행 금지** - requirements.txt에만 추가
2. requirements.txt 수정 후 반드시 사용자에게 설치 명령어 안내:
   ```
   requirements.txt에 패키지를 추가했습니다.
   아래 명령어로 설치해주세요:

   pip install -r requirements.txt
   ```
3. 특정 패키지만 설치할 경우:
   ```
   pip install 패키지명>=버전
   ```

---

## 트러블슈팅 기록 규칙

**에러를 디버깅하고 해결했을 때, 반드시 아래 형식으로 문서를 작성하세요.**
1. 상세 파일: `docs/troubleshooting/NNN-제목.md` 생성 (번호는 기존 파일 다음 번호)
2. README 업데이트: `docs/troubleshooting/README.md`에 요약 추가

위치: `docs/troubleshooting/`

### 파일 구조
- README.md: 요약
- 001-제목.md, 002-제목.md: 상세 (번호 순서대로 증가)

### README.md (요약)
```
## 001-제목
- 원인: 한 줄
- 해결: 한 줄
- 파일: 변경된 파일

---

## 배운 점
1. 배운 점 1
2. 배운 점 2
```

### 상세 파일 템플릿
```
# 제목

## 문제
- 증상, 에러

## 원인
- 분석

## 해결 과정 (시도는 여러 번일 수 있음)
### 시도 1: 방법명
- 파일: 경로:라인
- 변경 전: (코드)
- 변경 후: (코드)
- 결과: 성공/실패 (이유)

### 시도 N: ...

## 검증
- 테스트 입력
- 기대 결과
- 실제 결과
```
