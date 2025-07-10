# pages/1_요구정의.py

import streamlit as st
from core.persistence import get_all_projects, save_artifact, get_artifacts_for_project
from agents.gemini_agent import generate_problem_definition
import pandas as pd

st.set_page_config(page_title="요구사항 정의", layout="wide")
st.title("1. 요구사항 정의")
st.markdown("---")

# --- 1. 작업할 프로젝트 선택 ---
st.header("Step 1: 작업할 프로젝트 선택")
projects = get_all_projects()

if not projects:
    st.warning("진행 중인 프로젝트가 없습니다. 메인 대시보드에서 새 프로젝트를 먼저 생성해주세요.")
    st.stop()

# 프로젝트 이름 목록을 selectbox에 표시
project_names = [p[1] for p in projects]
selected_project_name = st.selectbox("프로젝트를 선택하세요.", project_names)

# 선택된 프로젝트의 ID 찾기
selected_project_id = [p[0] for p in projects if p[1] == selected_project_name][0]
st.info(f"선택된 프로젝트: **{selected_project_name}** (ID: {selected_project_id})")

# --- 2. 문제정의서 생성기 ---
st.header("Step 2: 문제정의서 생성")

# 3단 컬럼으로 정보 입력 UI 구성
col1, col2, col3 = st.columns(3)
with col1:
    use_case = st.text_area("사용 목적", "예: 고객센터로 인입되는 민원 텍스트를 유형별로 자동 분류", height=150)
with col2:
    background = st.text_area("도입 배경", "예: 현재 민원 처리가 수작업으로 이루어져 응답 시간이 길고, 상담사별 분류 기준이 달라 일관성이 떨어짐", height=150)
with col3:
    expected_effect = st.text_area("기대 효과", "예: 민원당 평균 응답 시간 20% 단축, 단순 반복 업무 감소로 인한 상담사 업무 만족도 향상", height=150)

if st.button("🤖 AI로 문제정의서 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 문제정의서를 작성하고 있습니다..."):
        prompt_input = {
            "use_case": use_case,
            "background": background,
            "expected_effect": expected_effect
        }
        # gemini_agent 호출
        generated_text = generate_problem_definition(prompt_input)
        
        # 결과를 session_state에 임시 저장하여 사용자에게 보여줌
        st.session_state['generated_problem_def'] = generated_text

# --- 3. 생성 결과 확인 및 저장 ---
if 'generated_problem_def' in st.session_state and st.session_state['generated_problem_def']:
    st.subheader("📝 생성된 문제정의서 초안")
    
    final_text = st.text_area("내용을 검토하고 수정하세요.", value=st.session_state.generated_problem_def, height=400)
    
    if st.button("💾 데이터베이스에 저장하기", use_container_width=True):
        # persistence 모듈을 사용하여 DB에 저장
        save_artifact(
            project_id=selected_project_id,
            stage="REQUIREMENT",
            type="PROBLEM_DEF",
            content=final_text
        )
        st.success(f"'{selected_project_name}' 프로젝트의 문제정의서가 성공적으로 저장되었습니다.")
        # 저장 후 임시 state 비우기
        del st.session_state['generated_problem_def']
        st.rerun()

# --- 4. 저장된 문서 이력 ---
st.markdown("---")
st.header("📜 저장된 문제정의서 이력")
artifacts = get_artifacts_for_project(selected_project_id, "PROBLEM_DEF")
if artifacts:
    for i, (content, created_at) in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({created_at})"):
            st.markdown(content)
else:
    st.info("이 프로젝트에 저장된 문제정의서가 없습니다.")
