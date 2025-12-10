"""
FastAPI 테스트 스크립트

로컬 서버가 실행 중이어야 합니다:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """루트 엔드포인트 테스트"""
    print("\n" + "="*60)
    print("TEST 1: 루트 엔드포인트")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print("✅ 성공")

def test_health():
    """헬스체크 테스트"""
    print("\n" + "="*60)
    print("TEST 2: 헬스체크")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ 성공")

def test_sql_query():
    """SQL 질문 테스트"""
    print("\n" + "="*60)
    print("TEST 3: SQL 질문 (직원 수)")
    print("="*60)
    
    payload = {"question": "직원은 총 몇 명인가요?"}
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Question: {result['question']}")
    print(f"Agent Type: {result['agent_type']}")
    print(f"Answer: {result['answer']}")
    print(f"Success: {result['success']}")
    
    assert response.status_code == 200
    assert result["agent_type"] == "SQL_AGENT"
    assert result["success"] == True
    print("✅ 성공")

def test_rag_query():
    """RAG 질문 테스트"""
    print("\n" + "="*60)
    print("TEST 4: RAG 질문 (연차 규정)")
    print("="*60)
    
    payload = {"question": "연차휴가는 몇일인가요?"}
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Question: {result['question']}")
    print(f"Agent Type: {result['agent_type']}")
    print(f"Answer: {result['answer']}")
    print(f"Success: {result['success']}")
    
    assert response.status_code == 200
    assert result["agent_type"] == "RAG_AGENT"
    assert result["success"] == True
    print("✅ 성공")

def test_multiple_queries():
    """여러 질문 연속 테스트"""
    print("\n" + "="*60)
    print("TEST 5: 연속 질문")
    print("="*60)
    
    questions = [
        ("평균 급여는?", "SQL_AGENT"),
        ("재택근무 가능한가요?", "RAG_AGENT"),
        ("부서별 직원 수는?", "SQL_AGENT"),
        ("복지 제도 알려줘", "RAG_AGENT"),
    ]
    
    for question, expected_agent in questions:
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json={"question": question}
        )
        result = response.json()
        agent_match = result["agent_type"] == expected_agent
        
        print(f"\n질문: {question}")
        print(f"  예상 Agent: {expected_agent}")
        print(f"  실제 Agent: {result['agent_type']} {'✅' if agent_match else '❌'}")
        print(f"  성공: {result['success']}")
        
        assert response.status_code == 200
    
    print("\n✅ 모든 연속 질문 성공")

if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("FastAPI 테스트 시작")
        print("="*60)
        
        test_root()
        test_health()
        test_sql_query()
        test_rag_query()
        test_multiple_queries()
        
        print("\n" + "="*60)
        print("✅ 모든 테스트 통과!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 서버에 연결할 수 없습니다.")
        print("서버를 먼저 실행하세요:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")

