# pages/2_문제정의.py

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_problem_definition, refine_content

# --- 페이지 제목 ---
st.title("📋 문제정의")
st.markdown("---")

# --- 프로젝트 선택 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("프로젝트를 선택해주세요. 메인 대시보드(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()
project_name = st.session_state.get('selected_project_name', 'N/A')
st.header(f"프로젝트: {project_name}")

# --- 문제정의서 생성기 ---
st.subheader("Step 1: 문제정의서 생성")
col1, col2, col3 = st.columns(3)
with col1:
    use_case = st.text_area("사용 목적", "예: 고객센터 민원 자동 분류", height=150)
with col2:
    background = st.text_area("도입 배경", "예: 수작업 처리로 인한 응답 시간 지연", height=150)
with col3:
    expected_effect = st.text_area("기대 효과", "예: 응답 시간 20% 단축", height=150)

if st.button("🤖 AI로 문제정의서 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 문제정의서를 작성하고 있습니다..."):
        prompt_input = {"use_case": use_case, "background": background, "expected_effect": expected_effect}
        generated_text = generate_problem_definition(prompt_input)
        st.session_state['generated_problem_def'] = generated_text
        st.rerun()

# --- 생성 결과 확인, 발전 및 저장 ---
if 'generated_problem_def' in st.session_state and st.session_state.get('generated_problem_def'):
    st.subheader("Step 2: 생성된 초안 발전시키기")
    st.session_state['generated_problem_def'] = st.text_area(
        "내용을 검토하고 직접 수정하거나, 아래 AI 도구를 사용해 보세요.", 
        value=st.session_state.generated_problem_def, 
        height=300,
        key="problem_def_editor"
    )
    # ... (AI 편집 도구모음 코드)
    
    st.subheader("Step 3: 최종본 저장")
    if st.button("💾 이 최종본을 데이터베이스에 저장하기", type="primary", use_container_width=True):
        save_artifact(
            project_id=selected_id,
            stage="REQUIREMENT",
            type="PROBLEM_DEF",
            content=st.session_state.problem_def_editor
        )
        st.success(f"'{project_name}' 프로젝트의 문제정의서가 성공적으로 저장되었습니다.")
        del st.session_state['generated_problem_def']
        st.rerun()

# --- 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 문제정의서 이력")
artifacts = get_artifacts_for_project(selected_id, "PROBLEM_DEF")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 문제정의서가 없습니다.")
