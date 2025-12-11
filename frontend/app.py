"""
Streamlit 채팅 UI for HR AI Agent

실행:
    streamlit run frontend/app.py
"""

import streamlit as st
import requests

API_URL = "http://api:8000/api/v1/query"  # FastAPI 서비스 이름(api) 기준

# 페이지 설정
st.set_page_config(
    page_title="HR AI Agent",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 헤더 (중앙 정렬)
st.markdown("""
<h1 style='text-align: center;'>🤖 Enterprise HR AI Agent</h1>
<p style='text-align: center;'><b>자연어로 질문하면 자동으로 SQL 실행하거나 사규 검색해드립니다</b></p>
""", unsafe_allow_html=True)

# 사이드바 - 정보
with st.sidebar:
    st.header("📊 시스템 정보")
    st.markdown("""
    ### Agent 종류
    - **SQL Agent**: 직원 데이터, 급여, 부서 정보
    - **RAG Agent**: 회사 규정, 복지, 휴가 제도
    
    ### 예시 질문
    
    **SQL 질문:**
    - 직원은 총 몇 명인가요?
    - 개발팀 평균 급여는?
    - 부서별 직원 수는?
    
    **RAG 질문:**
    - 연차휴가는 몇일인가요?
    - 재택근무 가능한가요?
    - 육아휴직 규정은?
    """)
    
    st.divider()
    
    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Agent 타입 뱃지 먼저 표시 (답변 위)
        if message["role"] == "assistant" and "agent_type" in message:
            agent_type = message["agent_type"]
            if agent_type == "SQL_AGENT":
                st.markdown(":blue[**🔷 SQL Agent**]")
            elif agent_type == "RAG_AGENT":
                st.markdown(":green[**📚 RAG Agent**]")

        # 답변 내용
        st.markdown(message["content"])

# 채팅 입력
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Agent 타입 뱃지 placeholder
        badge_placeholder = st.empty()
        answer_placeholder = st.empty()

        with st.spinner("생각 중..."):
            try:
                # FastAPI로 요청 보내기
                response = requests.post(API_URL, json={"question": prompt})
                data = response.json()

                if data.get("success"):
                    answer = data["answer"]
                    agent_type = data.get("agent_type")

                    # Agent 타입 뱃지 먼저 표시
                    if agent_type == "SQL_AGENT":
                        badge_placeholder.markdown(":blue[**🔷 SQL Agent**]")
                    elif agent_type == "RAG_AGENT":
                        badge_placeholder.markdown(":green[**📚 RAG Agent**]")

                    # 답변 표시
                    answer_placeholder.markdown(answer)

                    # 세션 저장
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "agent_type": agent_type
                    })

                else:
                    error_msg = f"❌ 오류 발생: {data.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

            except Exception as e:
                error_msg = f"❌ 서버 연결 실패: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# 푸터
st.divider()
st.caption("🔒 이 시스템은 데모용입니다. 실제 HR 데이터는 사용되지 않습니다.")