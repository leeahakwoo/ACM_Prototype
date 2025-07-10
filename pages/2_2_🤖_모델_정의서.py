# your_mcp_project/pages/2_2_🤖_모델_정의서.py

import streamlit as st
import google.generativeai as genai
import re

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("🤖 모델 정의서 작성")
st.markdown("---")

# session_state 의존성 확인 (선행 문서들이 작성되었는지 체크)
if 'problem_definition' not in st.session_state or not st.session_state.problem_definition.get('project_name'):
    st.error("먼저 '1_1_📝 문제 정의서' 페이지를 작성해주세요.")
    st.stop()
if 'data_spec' not in st.session_state or not st.session_state.data_spec.get('data_source'):
    st.error("먼저 '2_1_📈 데이터 정의서' 페이지를 작성해주세요.")
    st.stop()

# 모델 정의서 session_state 초기화
if 'model_spec' not in st.session_state:
    st.session_state['model_spec'] = {
        "model_name": "",
        "model_type": "분류",
        "key_features": "",
        "hyperparameters": ""
    }

# -------------------- 선행 문서 내용 확인 --------------------
st.header("1. 프로젝트 및 데이터 개요 확인")
with st.expander("저장된 문제 및 데이터 정의서 보기", expanded=False):
    st.markdown("**[문제 정의]**")
    st.json(st.session_state.problem_definition)
    st.markdown("**[데이터 정의]**")
    st.json(st.session_state.data_spec)

# -------------------- AI 모델 추천 기능 --------------------
st.header("✨ AI로 모델 사양 추천받기")
if GEMINI_ENABLED:
    if st.button("🚀 AI로 모델 사양 추천받기"):
        with st.spinner("Gemini가 프로젝트에 적합한 모델을 분석 및 추천 중입니다..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 이전 단계의 정보를 프롬프트에 포함하여 더 정확한 추천을 유도
            prompt = f"""
            당신은 시니어 AI 아키텍트입니다.
            아래에 제공된 '문제 정의서'와 '데이터 정의서' 내용을 바탕으로, 이 프로젝트에 가장 적합한 AI 모델의 사양을 추천해주세요.
            결과는 반드시 아래 형식을 정확히 지켜서, 각 항목에 대한 설명만 간결하게 작성해주세요.

            **[문제 정의서 요약]**
            - 프로젝트 목표: {st.session_state.problem_definition.get('project_goal')}
            - 핵심 결과물: {st.session_state.problem_definition.get('expected_output')}

            **[데이터 정의서 요약]**
            - 데이터 스키마: {st.session_state.data_spec.get('data_schema')}

            ---
            ### 모델 이름
            [여기에 추천 모델 이름 작성. 예: XGBoost 기반 이탈 예측 모델 v1.0]

            ### 모델 유형
            [분류, 회귀, 클러스터링, 자연어 처리, 이미지 인식, 기타 중 하나 선택]

            ### 주요 피처 (입력 변수)
            [위 데이터 스키마를 바탕으로 모델 학습에 중요할 것 같은 변수들을 나열]

            ### 주요 하이퍼파라미터
            [선택한 모델의 일반적인 추천 하이퍼파라미터 값들을 나열]
            """
            
            response = model.generate_content(prompt)
            
            try:
                # 간단한 파싱
                sections = response.text.split("###")
                st.session_state.model_spec['model_name'] = sections[1].split("\n", 1)[1].strip()
                st.session_state.model_spec['model_type'] = sections[2].split("\n", 1)[1].strip()
                st.session_state.model_spec['key_features'] = sections[3].split("\n", 1)[1].strip()
                st.session_state.model_spec['hyperparameters'] = sections[4].split("\n", 1)[1].strip()
                st.success("AI가 추천한 모델 사양을 아래 폼에 적용했습니다.")
            except Exception as e:
                st.error(f"AI 응답 파싱 실패: {e}")
                st.code(response.text)

# -------------------- 모델 정보 입력 폼 --------------------
st.markdown("---")
st.header("2. 모델 사양 정의")

with st.form("model_spec_form"):
    model_name = st.text_input(
        "모델 이름",
        value=st.session_state.model_spec.get("model_name", "")
    )
    model_type = st.selectbox(
        "모델 유형",
        ("분류", "회귀", "클러스터링", "자연어 처리", "이미지 인식", "기타"),
        index=("분류", "회귀", "클러스터링", "자연어 처리", "이미지 인식", "기타").index(st.session_state.model_spec.get("model_type", "분류"))
    )
    key_features = st.text_area(
        "주요 피처(입력 변수)",
        value=st.session_state.model_spec.get("key_features", ""),
        height=150
    )
    hyperparameters = st.text_area(
        "주요 하이퍼파라미터",
        value=st.session_state.model_spec.get("hyperparameters", ""),
        height=200
    )

    submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        st.session_state.model_spec['model_name'] = model_name
        st.session_state.model_spec['model_type'] = model_type
        st.session_state.model_spec['key_features'] = key_features
        st.session_state.model_spec['hyperparameters'] = hyperparameters
        st.success("모델 정의서 내용이 성공적으로 저장되었습니다!")
