# %%
# 셀 1: 환경 설정 및 모듈 임포트

import os
from dotenv import load_dotenv
from typing import TypedDict, Literal

# LangGraph
from langgraph.graph import StateGraph, END

# 우리 모듈
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router import Router
from core.sql_agent import SQLAgent
from core.rag_agent import RAGAgent

# 환경 변수 로드
load_dotenv()

print("✅ 모듈 임포트 완료")

# %%
# 셀 2: State 정의

class AgentState(TypedDict):
    """통합 Agent의 상태"""
    question: str           # 사용자 질문
    agent_type: str         # 선택된 Agent (SQL_AGENT | RAG_AGENT)
    sql_result: dict        # SQL Agent 결과
    rag_result: dict        # RAG Agent 결과
    final_answer: str       # 최종 답변
    error: str              # 오류 메시지

print("✅ AgentState 정의 완료")

# %%
# 셀 3: 노드 함수 정의 - Router

def route_node(state: AgentState) -> AgentState:
    """질문을 분석하여 Agent 선택"""
    router = Router()
    agent_type = router.route(state["question"])
    
    print(f"[Router] 질문: {state['question']}")
    print(f"[Router] 선택된 Agent: {agent_type}")
    
    state["agent_type"] = agent_type
    return state

print("✅ route_node 정의 완료")

# %%
# 셀 4: 노드 함수 정의 - SQL Agent

def sql_agent_node(state: AgentState) -> AgentState:
    """SQL Agent 실행"""
    print(f"[SQL Agent] 질문 처리 중...")
    
    try:
        agent = SQLAgent()
        result = agent.query(state["question"])
        
        state["sql_result"] = result
        
        # 최종 답변 생성
        if result["success"]:
            # 결과를 자연어로 변환
            if result["results"]:
                state["final_answer"] = f"SQL 조회 결과:\n{result['results']}"
            else:
                state["final_answer"] = "조회 결과가 없습니다."
        else:
            state["final_answer"] = f"SQL 실행 오류: {result.get('error', 'Unknown error')}"
            state["error"] = result.get("error", "")
        
        print(f"[SQL Agent] 완료")
        
    except Exception as e:
        state["error"] = str(e)
        state["final_answer"] = f"SQL Agent 오류: {str(e)}"
        print(f"[SQL Agent] 오류: {e}")
    
    return state

print("✅ sql_agent_node 정의 완료")

# %%
# 셀 5: 노드 함수 정의 - RAG Agent

def rag_agent_node(state: AgentState) -> AgentState:
    """RAG Agent 실행"""
    print(f"[RAG Agent] 질문 처리 중...")
    
    try:
        agent = RAGAgent()
        result = agent.query(state["question"])
        
        state["rag_result"] = result
        
        # 최종 답변 생성
        if result["success"]:
            state["final_answer"] = result["answer"]
        else:
            state["final_answer"] = f"RAG 검색 오류: {result.get('error', 'Unknown error')}"
            state["error"] = result.get("error", "")
        
        print(f"[RAG Agent] 완료")
        
    except Exception as e:
        state["error"] = str(e)
        state["final_answer"] = f"RAG Agent 오류: {str(e)}"
        print(f"[RAG Agent] 오류: {e}")
    
    return state

print("✅ rag_agent_node 정의 완료")

# %%
# 셀 6: 조건부 라우팅 함수

def route_to_agent(state: AgentState) -> Literal["sql_agent", "rag_agent"]:
    """Agent 타입에 따라 다음 노드 결정"""
    if state["agent_type"] == "SQL_AGENT":
        return "sql_agent"
    else:
        return "rag_agent"

print("✅ route_to_agent 정의 완료")

# %%
# 셀 7: LangGraph 구성

# StateGraph 생성
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("router", route_node)
workflow.add_node("sql_agent", sql_agent_node)
workflow.add_node("rag_agent", rag_agent_node)

# 엣지 추가
workflow.set_entry_point("router")

# 조건부 라우팅
workflow.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "sql_agent": "sql_agent",
        "rag_agent": "rag_agent"
    }
)

# Agent 실행 후 종료
workflow.add_edge("sql_agent", END)
workflow.add_edge("rag_agent", END)

# 그래프 컴파일
app = workflow.compile()

print("✅ LangGraph 구성 완료")

# %%
# 셀 8: 테스트 - SQL 질문

sql_question = "직원은 총 몇 명인가요?"

print(f"\n{'='*60}")
print(f"테스트 질문: {sql_question}")
print(f"{'='*60}\n")

initial_state = {
    "question": sql_question,
    "agent_type": "",
    "sql_result": {},
    "rag_result": {},
    "final_answer": "",
    "error": ""
}

result = app.invoke(initial_state)

print(f"\n{'='*60}")
print(f"최종 답변:")
print(result["final_answer"])
print(f"{'='*60}\n")

# %%
# 셀 9: 테스트 - RAG 질문

rag_question = "연차휴가는 몇일인가요?"

print(f"\n{'='*60}")
print(f"테스트 질문: {rag_question}")
print(f"{'='*60}\n")

initial_state = {
    "question": rag_question,
    "agent_type": "",
    "sql_result": {},
    "rag_result": {},
    "final_answer": "",
    "error": ""
}

result = app.invoke(initial_state)

print(f"\n{'='*60}")
print(f"최종 답변:")
print(result["final_answer"])
print(f"{'='*60}\n")

print("✅ 통합 그래프 실험 완료!")

# %%

