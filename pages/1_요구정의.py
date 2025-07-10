# pages/1_요구정의.py (최종 수정 버전)

import streamlit as st
from core.persistence import get_all_projects, save_artifact, get_artifacts_for_project
from agents.gemini_agent import generate_problem_definition

st.set_page_config(page_title="요구사항 정의", layout="wide")
st.title("1. 요구사항 정의")
st.markdown("---")

# --- 1. 작업할 프로젝트 선택 ---
st.header("Step 1: 작업할 프로젝트 선택")

# session_state에 선택된 프로젝트가 없으면 선택 유도
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None

projects = get_all_projects()

if not projects:
    st.warning("진행 중인 프로젝트가 없습니다. 메인 대시보드에서 새 프로젝트를 먼저 생성해주세요.")
    st.stop()

project_names = {p['id']: p['name'] for p in projects}
selected_id = st.selectbox(
    "프로젝트를 선택하세요.",
    options=list(project_names.keys()),
    format_func=lambda x: project_names[x],
    key='selected_project_id'
)

if selected_id:
    st.info(f"선택된 프로젝트: **{project_names[selected_id]}** (ID: {selected_id})")
    
    # (이하 UI 및 기능 코드는 이전과 거의 동일)
    st.header("Step 2: 문제정의서 생성")
    col1, col2, col3 = st.columns(3)
    with col1:
        use_case = st.text_area("사용 목적", "예: 고객센터로 인입되는 민원 텍스트를 유형별로 자동 분류", height=150)
    with col2:
        background = st.text_area("도입 배경", "예: 현재 민원 처리가 수작업으로 이루어져 응답 시간이 길고...", height=150)
    with col3:
        expected_effect = st.text_area("기대 효과", "예: 민원당 평균 응답 시간 20% 단축...", height=150)

    if st.button("🤖 AI로 문제정의서 생성하기", type="primary", use_container_width=True):
        with st.spinner("Gemini 에이전트가 문제정의서를 작성하고 있습니다..."):
            prompt_input = {"use_case": use_case, "background": background, "expected_effect": expected_effect}
            generated_text = generate_problem_definition(prompt_input)
            st.session_state['generated_problem_def'] = generated_text

    if 'generated_problem_def' in st.session_state and st.session_state['generated_problem_def']:
        st.subheader("📝 생성된 문제정의서 초안")
        final_text = st.text_area("내용을 검토하고 수정하세요.", value=st.session_state.generated_problem_def, height=400)
        if st.button("💾 데이터베이스에 저장하기", use_container_width=True):
            save_artifact(project_id=selected_id, stage="REQUIREMENT", type="PROBLEM_DEF", content=final_text)
            st.success("문제정의서가 성공적으로 저장되었습니다.")
            del st.session_state['generated_problem_def']
            st.rerun()

    st.markdown("---")
    st.header("📜 저장된 문제정의서 이력")
    artifacts = get_artifacts_for_project(selected_id, "PROBLEM_DEF")
    if artifacts:
        for i, artifact in enumerate(artifacts):
            with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
                st.markdown(artifact['content'])
    else:
        st.info("이 프로젝트에 저장된 문제정의서가 없습니다.")
