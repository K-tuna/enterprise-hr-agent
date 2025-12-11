# ENUM 값 매핑 오류

## 문제
- "김철수 휴가 몇 번?" → 2번 (실제는 1번)
- 생성된 SQL: `WHERE status = 'PRESENT'` (출근)
- 올바른 SQL: `WHERE status = 'VACATION'` (휴가)

## 원인
- 스키마에 ENUM 가능한 값이 표시되지 않음
- LLM이 `status` 컬럼에 어떤 값이 있는지 모름
- 샘플 데이터 3개에 `VACATION`이 없어서 추측 불가

스키마 출력 (당시):
```
TABLE attendance:
  - status (enum)
  샘플 데이터:
    (1, 1, '2024-01-02', '08:55:00', '18:10:00', 'PRESENT')
    (2, 1, '2024-01-03', '09:15:00', '18:30:00', 'LATE')
    (3, 1, '2024-01-04', '08:50:00', '18:00:00', 'PRESENT')
```
→ VACATION이 샘플에 없음

## 해결 과정

### 시도 1: 샘플 개수 늘리기
- 3개 → 5개로 늘리면 VACATION이 포함될 수 있음
- 결과: 검토만 (데이터 순서에 따라 여전히 누락 가능, 근본 해결 아님)

### 시도 2: ENUM 값 명시
- 파일: `core/database/connection.py:120-140`
- 변경 전:
```python
columns = conn.execute(
    text(
        f"""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{db_name}'
    AND TABLE_NAME = '{table_name}'
    ORDER BY ORDINAL_POSITION
    """
    )
).fetchall()

for col_name, data_type in columns:
    schema_text += f"  - {col_name} ({data_type})\n"
```
- 변경 후:
```python
columns = conn.execute(
    text(
        f"""
    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{db_name}'
    AND TABLE_NAME = '{table_name}'
    ORDER BY ORDINAL_POSITION
    """
    )
).fetchall()

for col_name, data_type, column_type in columns:
    if data_type == "enum":
        # ENUM 값 표시: enum('A','B','C') → (enum: A, B, C)
        enum_values = column_type.replace("enum(", "").replace(")", "").replace("'", "")
        schema_text += f"  - {col_name} (enum: {enum_values})\n"
    else:
        schema_text += f"  - {col_name} ({data_type})\n"
```
- 결과: 성공

스키마 출력 (수정 후):
```
TABLE attendance:
  - status (enum: PRESENT, LATE, ABSENT, VACATION)
```

## 검증
- 테스트 입력: "김철수 휴가 몇 번?"
- 기대 결과: SQL에 `status = 'VACATION'` 사용, 답변 1번
- 실제 결과:
  - SQL: `SELECT COUNT(*) FROM attendance WHERE emp_id = 1 AND status = 'VACATION';` ✅
  - 답변: "김철수는 휴가를 1번 갔습니다." ✅
