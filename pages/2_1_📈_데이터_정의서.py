# your_mcp_project/pages/2_1_📈_데이터_정의서.py

import streamlit as st
import google.generativeai as genai

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# 페이지 설정 및 초기화
st.title("📈 데이터 정의서 작성")
st.markdown("---")

# session_state 의존성 확인
if 'problem_definition' not in st.session_state or not st.session_state.problem_definition.get('project_name'):
    st.error("먼저 '📝 문제 정의서' 페이지를 작성해주세요.")
    st.stop()

# 데이터 정의서 session_state 초기화
if 'data_spec' not in st.session_state:
    st.session_state['data_spec'] = {
        "data_source": "",
        "data_schema": "",
        "preprocessing_steps": "",
        "privacy_issues": ""
    }

# AI 초안 생성 기능
st.header("✨ AI로 빠르게 초안 작성하기")
if GEMINI_ENABLED:
    data_description = st.text_input("사용할 데이터에 대해 간단히 설명해주세요.", placeholder="예: 온라인 쇼핑몰의 고객 정보 및 구매 기록 데이터")
    
    if st.button("🚀 AI로 데이터 정의서 초안 생성", disabled=not data_description):
        with st.spinner("Gemini가 데이터 정의서 초안을 작성 중입니다..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            당신은 데이터 분석 전문가입니다.
            다음 설명을 바탕으로 '데이터 정의서'의 각 항목에 대한 내용을 구체적으로 작성해주세요.
            결과는 반드시 아래 형식을 정확히 지켜서, 각 항목에 대한 설명만 간결하게 작성해주세요.

            **데이터 설명:** "{data_description}"

            ---
            ### 데이터 출처 및 수집 방법
            [여기에 내용 작성]

            ### 데이터 스키마 (주요 컬럼 및 설명)
            [여기에 내용 작성, 마크다운 테이블 형식 권장]

            ### 주요 전처리 단계
            [여기에 내용 작성, 순서가 있는 목록 형식 권장]

            ### 개인정보 및 민감정보 관련 이슈
            [여기에 내용 작성]
            """
            response = model.generate_content(prompt)
            # 간단한 파싱 (향후 정규식으로 고도화 가능)
            try:
                sections = response.text.split("###")
                st.session_state.data_spec['data_source'] = sections[1].split("\n", 1)[1].strip()
                st.session_state.data_spec['data_schema'] = sections[2].split("\n", 1)[1].strip()
                st.session_state.data_spec['preprocessing_steps'] = sections[3].split("\n", 1)[1].strip()
                st.session_state.data_spec['privacy_issues'] = sections[4].split("\n", 1)[1].strip()
                st.success("AI가 생성한 초안을 아래 폼에 적용했습니다.")
            except Exception as e:
                st.error(f"AI 응답 파싱 실패: {e}")
                st.code(response.text)

# 데이터 정의서 입력 폼
st.markdown("---")
st.header("📄 데이터 정의서 상세 내용")

with st.form("data_spec_form"):
    data_source = st.text_area(
        "데이터 출처 및 수집 방법",
        value=st.session_state.data_spec.get("data_source", ""),
        height=100,
        help="예: 사내 데이터베이스(PostgreSQL)의 'orders'와 'users' 테이블을 Join하여 일별로 추출"
    )
    data_schema = st.text_area(
        "데이터 스키마 (주요 컬럼 및 설명)",
        value=st.session_state.data_spec.get("data_schema", ""),
        height=200,
        help="컬럼명, 데이터 타입, 설명을 마크다운 테이블 형식으로 작성하면 가독성이 좋습니다."
    )
    preprocessing_steps = st.text_area(
        "주요 전처리 단계",
        value=st.session_state.data_spec.get("preprocessing_steps", ""),
        height=150,
        help="결측치 처리, 이상치 제거, 스케일링, 인코딩 등 수행할 작업을 순서대로 나열합니다."
    )
    privacy_issues = st.text_area(
        "개인정보 및 민감정보 관련 이슈",
        value=st.session_state.data_spec.get("privacy_issues", ""),
        height=100,
        help="개인정보보호법에 따른 비식별화 조치(마스킹, 해싱 등) 내역을 기술합니다."
    )

    submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        st.session_state.data_spec['data_source'] = data_source
        st.session_state.data_spec['data_schema'] = data_schema
        st.session_state.data_spec['preprocessing_steps'] = preprocessing_steps
        st.session_state.data_spec['privacy_issues'] = privacy_issues
        st.success("데이터 정의서가 성공적으로 저장되었습니다!")
