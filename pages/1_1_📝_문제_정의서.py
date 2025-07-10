# your_mcp_project/pages/1_1_📝_문제_정의서.py
# (UI/UX 개선 버전)

import streamlit as st
import google.generativeai as genai
import json
import re

# ... (Gemini API 설정 및 페이지 기본 설정은 이전과 동일) ...
# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    st.error("❗ Gemini API 키가 설정되지 않았습니다. Streamlit Cloud의 'Secrets'에 API 키를 추가해주세요.")
    GEMINI_ENABLED = False

# 페이지 설정 및 초기화
st.title("📝 문제 정의서 (AI Wizard)")
st.markdown("---")

states_to_initialize = {
    'problem_definition': {
        "project_name": "", "project_goal": "", "problem_background": "", "expected_output": ""
    },
    'pd_messages': []
}
for key, value in states_to_initialize.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- 대화형 AI Wizard UI (개선된 구조) --------------------
st.header("✨ 1단계: AI와 대화하며 프로젝트 구상하기")

# 대화 영역을 컨테이너로 묶어 시각적으로 분리
with st.container(height=400): # 고정된 높이를 주어 스크롤바 생성
    # AI의 첫 질문
    if not st.session_state.pd_messages:
        st.session_state.pd_messages.append(
            {"role": "assistant", "content": "안녕하세요! AI 프로젝트 기획을 도와드릴게요. 어떤 문제를 해결하고 싶으신가요? 핵심 아이디어를 자유롭게 말씀해주세요."}
        )
    
    # 이전 대화 기록 표시
    for message in st.session_state.pd_messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "🧑‍💻"):
            st.markdown(message["content"])

# 사용자 입력 처리 (st.chat_input은 컨테이너 밖에 위치)
if user_prompt := st.chat_input("여기에 답변을 입력하세요...", disabled=not GEMINI_ENABLED):
    # 사용자 메시지 기록 및 표시
    st.session_state.pd_messages.append({"role": "user", "content": user_prompt})
    
    # AI 응답 생성
    with st.spinner("AI가 답변을 생각 중입니다..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.pd_messages])
        prompt_for_ai = f"""
        당신은 친절한 AI 프로젝트 기획 어시스턴트입니다. 다음 대화 내용을 바탕으로 자연스럽게 대화를 이어가세요.
        [대화 기록]\n{conversation_history}\n[당신의 다음 응답]
        """
        response = model.generate_content(prompt_for_ai)
        ai_response = response.text
    
    # AI 응답 기록
    st.session_state.pd_messages.append({"role": "assistant", "content": ai_response})
    
    # 페이지를 새로고침하여 전체 대화 업데이트
    st.rerun()

# -------------------- 문서 생성 기능 --------------------
st.markdown("---")
st.header("✨ 2단계: 대화 내용으로 문서 초안 생성하기")

if len(st.session_state.pd_messages) > 1:
    if st.button("💬 문서 초안 생성하기", type="primary", use_container_width=True, disabled=not GEMINI_ENABLED):
        # (이전 코드와 동일한 문서 생성 로직)
        with st.spinner("AI가 대화 내용을 종합하여 문서 초안을 작성합니다..."):
            # ... (이전과 동일한 Gemini JSON 생성 로직) ...
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


# -------------------- 최종 결과 확인 및 저장 --------------------
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
