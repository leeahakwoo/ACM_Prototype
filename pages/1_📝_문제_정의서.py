# your_mcp_project/pages/1_📝_문제_정의서.py
# (수정된 최종 코드)

import streamlit as st
import google.generativeai as genai
import re # 응답 텍스트를 파싱하기 위해 정규식 라이브러리 임포트

# -------------------- Gemini API 설정 --------------------
# st.secrets를 통해 API 키를 안전하게 불러옵니다.
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 (기존과 동일) --------------------
st.title("📝 문제 정의서 작성")
st.markdown("---")

if 'problem_definition' not in st.session_state:
    st.session_state['problem_definition'] = {
        "project_name": "",
        "project_goal": "",
        "problem_background": "",
        "expected_output": ""
    }

# -------------------- AI 초안 생성 기능 --------------------
st.header("✨ AI로 빠르게 초안 작성하기")

# Gemini API 키가 설정되었는지 확인
if not GEMINI_ENABLED:
    st.error("Gemini API 키가 설정되지 않았습니다. st.secrets에 API 키를 추가해주세요.")
else:
    # 템플릿 함수: Gemini API의 응답을 파싱하여 session_state에 저장
    def parse_and_save_response(response_text):
        try:
            # 정규식을 사용하여 각 섹션의 내용을 추출
            goal = re.search(r"### 프로젝트의 최종 목표\s*\n(.*?)\n###", response_text, re.DOTALL).group(1).strip()
            background = re.search(r"### 문제 배경 및 필요성\s*\n(.*?)\n###", response_text, re.DOTALL).group(1).strip()
            output = re.search(r"### 핵심 결과물\s*\n(.*?)$", response_text, re.DOTALL).group(1).strip()
            
            # session_state 업데이트
            st.session_state.problem_definition['project_goal'] = goal
            st.session_state.problem_definition['problem_background'] = background
            st.session_state.problem_definition['expected_output'] = output
            
            st.success("AI가 생성한 초안을 아래 폼에 적용했습니다. 내용을 확인하고 수정해주세요.")
        except Exception as e:
            st.error(f"AI 응답을 파싱하는 데 실패했습니다. 원본 응답을 확인해주세요:\n\n{response_text}")

    # AI 초안 생성을 위한 입력
    idea_input = st.text_input("프로젝트의 핵심 아이디어를 입력하세요", placeholder="예: 온라인 쇼핑몰 고객들의 이탈 원인을 분석하고 싶다.")
    
    if st.button("🚀 AI로 초안 생성하기", disabled=not idea_input):
        with st.spinner("Gemini가 문서를 작성하는 중입니다... 잠시만 기다려주세요."):
            # Gemini 모델 선택 및 프롬프트 정의
            model = genai.GenerativeModel('gemini-1.5-flash') # 빠르고 효율적인 모델 사용
            
            prompt = f"""
            당신은 AI 프로젝트 기획 전문가입니다.
            다음 핵심 아이디어를 바탕으로 'AI 개발 문제 정의서'의 각 항목에 대한 내용을 구체적이고 전문적인 초안으로 작성해주세요.
            결과는 반드시 아래 형식을 정확히 지켜서, 각 항목에 대한 설명만 간결하게 작성해주세요.

            **핵심 아이디어:** "{idea_input}"

            ---
            ### 프로젝트의 최종 목표
            [여기에 목표 작성]

            ### 문제 배경 및 필요성
            [여기에 배경 및 필요성 작성]

            ### 핵심 결과물
            [여기에 결과물 작성]
            """
            
            # API 호출
            response = model.generate_content(prompt)
            
            # 응답 파싱 및 저장
            parse_and_save_response(response.text)


# -------------------- 입력 폼 (기존과 거의 동일) --------------------
st.markdown("---")
st.header("📄 문제 정의서 상세 내용")
st.info("AI가 생성한 초안을 검토하고 수정하거나, 직접 내용을 입력해주세요.", icon="ℹ️")

with st.form("problem_definition_form"):
    project_name = st.text_input(
        "프로젝트 이름",
        value=st.session_state.problem_definition.get("project_name", ""),
        help="예: 고객 이탈 예측 AI 모델"
    )
    # AI가 생성한 값으로 채워지도록 key를 사용
    project_goal = st.text_area("프로젝트의 최종 목표", height=100, key="pd_goal_key")
    problem_background = st.text_area("문제 배경 및 필요성", height=200, key="pd_background_key")
    expected_output = st.text_area("핵심 결과물 (Key Deliverables)", height=100, key="pd_output_key")

    submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        st.session_state.problem_definition['project_name'] = project_name
        # st.form 내부 위젯은 session_state에 직접 연결되지 않으므로, 제출 시 다시 할당해줍니다.
        st.session_state.problem_definition['project_goal'] = project_goal
        st.session_state.problem_definition['problem_background'] = problem_background
        st.session_state.problem_definition['expected_output'] = expected_output

        st.success("문제 정의서 내용이 성공적으로 저장되었습니다!")
        st.balloons()

# -------------------- 저장된 데이터 확인 (기존과 동일) --------------------
# ... (기존 코드와 동일하여 생략) ...
