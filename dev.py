# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DATABASE_URL이 없으면 기본값 설정
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "mysql+pymysql://user:password@localhost:3306/enterprise_hr_db?charset=utf8mb4"

# 프로젝트 루트 path 추가
sys.path.insert(0, ".")

# ===========================================
# 여기서부터 테스트 코드 작성
# ===========================================

from core.container import init_container
from app.core.config import get_settings

settings = get_settings()
print(f"[DEBUG] LLM Model: {settings.LLM_MODEL}")

# Container 초기화
container = init_container(settings)
print("[DEBUG] Container 초기화 완료")

# dev.py에 추가
# print(f"스키마: {container.db.get_table_schema()}")
# Router 테스트
# router = container.router
#result = router.route("직원 수는?")
#print(f"[DEBUG] Router 테스트: {result}")

# SQL Agent 테스트
sql_agent = container.sql_agent
result = sql_agent.query("김철수 휴가 몇번?")
print(f"답변: {result['answer']}")
print(f"SQL: {result['metadata']['sql']}")
print(f"결과: {result['metadata']['results']}")

# RAG Agent 테스트
# rag_agent = container.rag_agent
# result = rag_agent.query("연차휴가는 며칠인가요?")
# print(f"답변: {result['answer']}")
# print(f"출처: {result['metadata']['source_docs']}")
# print(f"성공: {result['success']}")

# HR Agent 통합 테스트
# hr_agent = container.hr_agent
# result = hr_agent.query("직원 수는?")
# print(f"[DEBUG] HR Agent 결과: {result}")
