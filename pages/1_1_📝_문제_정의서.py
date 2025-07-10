# your_mcp_project/pages/1_1_📝_문제_정의서.py
# (st.chat_input 대신 커스텀 입력창을 사용한 최종 버전)

import streamlit as st
import google.generativeai as genai
import json
import re

# -------------------- Gemini API 설정 --------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    st.error("❗ Gemini API 키가 설정되지 않았습니다. Streamlit Cloud의 'Secrets'에 API 키를 추가해주세요.")
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("📝 문제 정의서 (AI Wizard)")
st.markdown("---")

states_to_initialize = {
    'problem_definition': {
        "project_name": "", "project_goal": "", "problem_background": "", "expected_output": ""
    },
    'pd_messages': [],
    'user_input': '' # 사용자 입력을 담을 임시 state
}
for key, value in states_to_initialize.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- 1단계: 대화형 AI Wizard UI --------------------
st.header("✨ 1단계: AI와 대화하며 프로젝트 구상하기")

# 대화 영역 (스크롤 가능)
chat_container = st.container(height=400)

with chat_container:
    # AI의 첫 질문
    if not st.session_state.pd_messages:
        st.session_state.pd_messages.append(
            {"role": "assistant", "content": "안녕하세요! AI 프로젝트 기획을 도와드릴게요. 어떤 문제를 해결하고 싶으신가요? 핵심 아이디어를 자유롭게 말씀해주세요."}
        )
    
    # 이전 대화 기록 표시
    for message in st.session_state.pd_messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "🧑‍💻"):
            st.markdown(message["content"])

# --- 커스텀 채팅 입력창 (핵심 수정 부분) ---
def handle_user_input():
    user_prompt = st.session_state.user_input
    if user_prompt and GEMINI_ENABLED:
        # 1. 사용자 메시지를 기록에 추가
        st.session_state.pd_messages.append({"role": "user", "content": user_prompt})
        
        # 2. AI 응답 생성
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.pd_messages])
            prompt_for_ai = f"""
            당신은 친절한 AI 프로젝트 기획 어시스턴트입니다. 다음 대화 내용을 바탕으로 자연스럽게 대화를 이어가세요.
            [대화 기록]\n{conversation_history}\n[당신의 다음 응답]
            """
            response = model.generate_content(prompt_for_ai)
            ai_response = response.text
        except Exception as e:
            ai_response = f"죄송합니다, AI 응답 생성 중 오류가 발생했습니다: {e}"
        
        # 3. AI 응답을 기록에 추가
        st.session_state.pd_messages.append({"role": "assistant", "content": ai_response})
        
        # 4. 입력창 비우기
        st.session_state.user_input = ""

# st.text_area와 st.button을 가로로 배치
col1, col2 = st.columns([4, 1])
with col1:
    st.text_area(
        "AI에게 답변하기", 
        key="user_input", 
        label_visibility="collapsed",
        placeholder="AI에게 답변하기...",
        on_change=handle_user_input # Enter 키로도 제출되도록 on_change 콜백 사용
    )
with col2:
    st.button("전송", on_click=handle_user_input, use_container_width=True, type="primary")

# --- (이하 2, 3단계 코드는 이전과 동일) ---
# -------------------- 2단계: 문서 생성 기능 --------------------
st.markdown("---")
st.header("✨ 2단계: 대화 내용으로 문서 초안 생성하기")

if len(st.session_state.pd_messages) > 1:
    if st.button("💬 문서 초안 생성하기", type="secondary", use_container_width=True, disabled=not GEMINI_ENABLED):
        with st.spinner("AI가 대화 내용을 종합하여 문서 초안을 작성합니다..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.pd_messages])
            prompt_for_json = f"""
            당신은 대화 내용을 분석하여 공식 문서로 정리하는 뛰어난 요약 전문가입니다.
            아래 대화 기록을 바탕으로 '문제 정의서'의 각 항목을 채워주세요.
            결과는 반드시 아래의 JSON 형식으로만 응답해야 합니다.

            [대화 기록]
            {conversation_history}

            ```json
            {{
                "project_name": "[프로젝트의 특성을 잘 나타내는 이름]",
                "project_goal": "[프로젝트의 최종 목표]",
                "problem_background": "[이 문제가 왜 중요하고 해결해야 하는지에 대한 배경]",
                "expected_output": "[프로젝트의 구체적인 결과물]"
            }}
            ```
            """
            try:
                response = model.generate_content(prompt_for_json)
                match = re.search(r"```json\s*(\{.*?\})\s*```", response.text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    parsed_data = json.loads(json_str)
                    st.session_state.problem_definition.update(parsed_data)
                    st.success("초안 생성 완료! 아래 3단계에서 내용을 확인하고 저장하세요.")
                else:
                    st.error("AI의 응답에서 유효한 JSON 형식을 찾지 못했습니다.")
                    st.code(response.text)
            except Exception as e:
                st.error(f"문서 생성 중 오류 발생: {e}")
        st.rerun()
else:
    st.info("AI와 한 번 이상 대화해야 문서 초안을 생성할 수 있습니다.")

# -------------------- 3단계: 최종 결과 확인 및 저장 --------------------
st.markdown("---")
st.header("✨ 3단계: 최종 결과 확인 및 저장하기")
with st.form("problem_definition_form"):
    project_name = st.text_input("프로젝트 이름", value=st.session_state.problem_definition.get("project_name", ""))
    project_goal = st.text_area("프로젝트의 최종 목표", value=st.session_state.problem_definition.get("project_goal", ""), height=100)
    problem_background = st.text_area("문제 배경 및 필요성", value=st.session_state.problem_definition.get("problem_background", ""), height=200)
    expected_output = st.text_area("핵심 결과물", value=st.session_state.problem_definition.get("expected_output", ""), height=100)
    
    if st.form_submit_button("💾 이 내용으로 저장하기", use_container_width=True):
        st.session_state.problem_definition.update({
            "project_name": project_name, "project_goal": project_goal,
            "problem_background": problem_background, "expected_output": expected_output
        })
        st.success("문제 정의서가 성공적으로 저장되었습니다!")
