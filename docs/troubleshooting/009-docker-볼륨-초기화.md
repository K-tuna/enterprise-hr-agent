# 009-docker-볼륨-초기화

## 증상
```bash
docker-compose down -v
docker-compose up -d
```
실행 후에도 DB 데이터가 그대로 남아있음 (기존 4명 → 15명으로 변경했는데 반영 안 됨)

## 원인
바인드 마운트(`./data/mysql_data`) 사용 중이었음.
`docker-compose down -v`는 **네임드 볼륨**만 삭제함.

### 바인드 마운트 vs 네임드 볼륨
| 구분 | 바인드 마운트 | 네임드 볼륨 |
|------|--------------|------------|
| 문법 | `./data/mysql_data:/var/lib/mysql` | `mysql_data:/var/lib/mysql` |
| 저장 위치 | 호스트 디렉토리 직접 지정 | Docker가 관리 (`/var/lib/docker/volumes/`) |
| `down -v` | ❌ 삭제 안 됨 | ✅ 삭제됨 |
| 용도 | 개발 중 코드 동기화 | DB, 캐시 등 영속 데이터 |

## 해결
`docker-compose.yml` 수정:

**Before:**
```yaml
services:
  db:
    volumes:
      - ./data/mysql_data:/var/lib/mysql
```

**After:**
```yaml
services:
  db:
    volumes:
      - mysql_data:/var/lib/mysql
      - ./data/db_init:/docker-entrypoint-initdb.d

volumes:
  mysql_data:
```

## 적용
```bash
# 기존 바인드 마운트 디렉토리 삭제 (필요시)
rm -rf ./data/mysql_data

# 재시작
docker-compose down -v
docker-compose up -d
```

## 검증
```sql
SELECT COUNT(*) FROM employees;  -- 15 ✅
```

## 교훈
- DB 데이터는 네임드 볼륨 사용 (업계 표준)
- 코드/설정 파일만 바인드 마운트 사용
- `docker-compose.yml` 구조: `services` → `networks` → `volumes` 순서
