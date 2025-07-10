# your_mcp_project/pages/1_📝_문제_정의서.py
# (수정된 최종 코드)

import streamlit as st
import google.generativeai as genai
import re

# -------------------- Gemini API 설정 --------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
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

if not GEMINI_ENABLED:
    st.error("Gemini API 키가 설정되지 않았습니다. Streamlit Cloud의 'Secrets'에 API 키를 추가해주세요.")
else:
    def parse_and_save_response(response_text):
        try:
            # 정규식을 사용하여 각 섹션의 내용을 더 안정적으로 추출
            goal = re.search(r"###\s*프로젝트의 최종 목표\s*\n(.*?)(?=\n###|$)", response_text, re.DOTALL).group(1).strip()
            background = re.search(r"###\s*문제 배경 및 필요성\s*\n(.*?)(?=\n###|$)", response_text, re.DOTALL).group(1).strip()
            output = re.search(r"###\s*핵심 결과물\s*\n(.*?)(?=\n###|$)", response_text, re.DOTALL).group(1).strip()
            
            st.session_state.problem_definition['project_goal'] = goal
            st.session_state.problem_definition['problem_background'] = background
            st.session_state.problem_definition['expected_output'] = output
            
            st.success("AI가 생성한 초안을 아래 폼에 적용했습니다. 내용을 확인하고 수정해주세요.")
            
        except Exception as e:
            st.error(f"AI 응답을 파싱하는 데 실패했습니다. 아래 원본 응답을 확인하고 직접 내용을 복사-붙여넣기 해주세요. (오류: {e})")

    idea_input = st.text_input("프로젝트의 핵심 아이디어를 입력하세요", placeholder="예: 온라인 쇼핑몰 고객들의 이탈 원인을 분석하고 싶다.")
    
    if st.button("🚀 AI로 초안 생성하기", disabled=not idea_input):
        with st.spinner("Gemini가 문서를 작성하는 중입니다... 잠시만 기다려주세요."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            당신은 AI 프로젝트 기획 전문가입니다.
            다음 핵심 아이디어를 바탕으로 'AI 개발 문제 정의서'의 각 항목에 대한 내용을 구체적이고 전문적인 초안으로 작성해주세요.
            결과는 반드시 아래 형식을 정확히 지켜서, 각 항목에 대한 설명만 간결하게 작성해주세요. 각 항목은 '###'으로 시작해야 합니다.

            **핵심 아이디어:** "{idea_input}"

            ---
            ### 프로젝트의 최종 목표
            [여기에 목표 작성]

            ### 문제 배경 및 필요성
            [여기에 배경 및 필요성 작성]

            ### 핵심 결과물
            [여기에 결과물 작성]
            """
            
            response = model.generate_content(prompt)
            
            # **[디버깅용]** AI의 원본 응답을 화면에 출력합니다.
            if response and response.text:
                st.markdown("---")
                st.subheader("🤖 Gemini 원본 응답 (디버깅용)")
                st.code(response.text, language='markdown')
                st.markdown("---")
                parse_and_save_response(response.text)
            else:
                st.error("Gemini로부터 응답을 받지 못했습니다. API 키나 네트워크 상태를 확인해주세요.")

# -------------------- 입력 폼 (수정된 부분) --------------------
st.markdown("---")
st.header("📄 문제 정의서 상세 내용")
st.info("AI가 생성한 초안을 검토하고 수정하거나, 직접 내용을 입력해주세요.", icon="ℹ️")

with st.form("problem_definition_form"):
    # session_state 값을 value에 직접 연결합니다.
    project_name = st.text_input(
        "프로젝트 이름",
        value=st.session_state.problem_definition.get("project_name", ""),
        help="예: 고객 이탈 예측 AI 모델"
    )
    project_goal = st.text_area(
        "프로젝트의 최종 목표",
        value=st.session_state.problem_definition.get("project_goal", ""), # ★★★ 핵심 수정 사항
        height=100
    )
    problem_background = st.text_area(
        "문제 배경 및 필요성",
        value=st.session_state.problem_definition.get("problem_background", ""), # ★★★ 핵심 수정 사항
        height=200
    )
    expected_output = st.text_area(
        "핵심 결과물 (Key Deliverables)",
        value=st.session_state.problem_definition.get("expected_output", ""), # ★★★ 핵심 수정 사항
        height=100
    )

    submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        st.session_state.problem_definition['project_name'] = project_name
        st.session_state.problem_definition['project_goal'] = project_goal
        st.session_state.problem_definition['problem_background'] = problem_background
        st.session_state.problem_definition['expected_output'] = expected_output

        st.success("문제 정의서 내용이 성공적으로 저장되었습니다!")
        st.balloons()

# -------------------- 저장된 데이터 확인 (기존과 동일) --------------------
st.markdown("---")
st.header("2. 현재 저장된 내용 확인")
with st.expander("저장된 문제 정의서 보기"):
    if any(st.session_state.problem_definition.values()):
        st.json(st.session_state.problem_definition)
    else:
        st.warning("아직 저장된 내용이 없습니다. 위의 폼을 작성하고 '저장하기' 버튼을 눌러주세요.")
