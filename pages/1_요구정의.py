# pages/1_요구정의.py

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project, get_all_projects
from gemini_agent import generate_problem_definition

st.set_page_config(page_title="요구사항 정의", layout="wide")
st.title("📋 요구사항 정의")
st.markdown("---")

# --- 1. 선택된 프로젝트 정보 확인 ---
# session_state에서 선택된 프로젝트 ID를 가져옴
selected_id = st.session_state.get('selected_project_id', None)

if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

# 선택된 프로젝트의 이름 찾기
projects = get_all_projects()
project_name = next((p['name'] for p in projects if p['id'] == selected_id), "알 수 없음")
st.header(f"프로젝트: {project_name}")
st.caption(f"(Project ID: {selected_id})")

# --- 2. 문제정의서 생성기 ---
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

# --- 3. 생성 결과 확인, 발전 및 저장 ---
if 'generated_problem_def' in st.session_state and st.session_state['generated_problem_def']:
    st.subheader("📝 생성된 문제정의서 초안")
    
    # st.text_area에 key를 부여하여 현재 값을 쉽게 참조하고 업데이트할 수 있도록 함
    st.session_state['generated_problem_def'] = st.text_area(
        "내용을 검토하고 수정하세요.", 
        value=st.session_state.generated_problem_def, 
        height=300,
        key="problem_def_editor"
    )

    st.markdown("---")
    st.subheader("🤖 AI 편집 도구모음")
    st.info("아래 버튼과 입력창을 통해 AI와 함께 문서의 완성도를 높여보세요.")

    # 버튼들을 가로로 배치
    col1, col2, col3 = st.columns(3)
    current_text = st.session_state.problem_def_editor # 현재 편집 중인 텍스트
    
    with col1:
        if st.button("✨ 전문가처럼 다듬기", use_container_width=True):
            with st.spinner("AI가 문체를 다듬고 있습니다..."):
                instruction = "이 내용을 더 논리적이고 전문적인 보고서 형식으로 다듬어줘."
                refined_text = refine_content(current_text, instruction)
                st.session_state.generated_problem_def = refined_text
                st.rerun()

    with col2:
        if st.button("🤏 간결하게 요약하기", use_container_width=True):
            with st.spinner("AI가 내용을 요약하고 있습니다..."):
                instruction = "이 내용의 핵심만 남기고 3~4문장으로 간결하게 요약해줘."
                refined_text = refine_content(current_text, instruction)
                st.session_state.generated_problem_def = refined_text
                st.rerun()

    with col3:
        if st.button("🔍 상세하게 확장하기", use_container_width=True):
            with st.spinner("AI가 내용을 상세화하고 있습니다..."):
                instruction = "이 내용의 각 항목에 대해, 더 구체적인 예시나 설명을 덧붙여서 내용을 풍부하게 만들어줘."
                refined_text = refine_content(current_text, instruction)
                st.session_state.generated_problem_def = refined_text
                st.rerun()

    # 직접 지시하기 기능
    custom_instruction = st.text_input("직접 편집 지시하기 (예: 이 내용을 격식있는 메일 형식으로 바꿔줘)")
    if st.button("실행", disabled=not custom_instruction):
        with st.spinner("AI가 당신의 지시를 수행하고 있습니다..."):
            refined_text = refine_content(current_text, custom_instruction)
            st.session_state.generated_problem_def = refined_text
            st.rerun()

    st.markdown("---")
    # 최종 저장 버튼
    if st.button("💾 이 최종본을 데이터베이스에 저장하기", type="primary", use_container_width=True):
        save_artifact(
            project_id=selected_id,
            stage="REQUIREMENT",
            type="PROBLEM_DEF",
            content=current_text # 최종적으로 편집된 내용을 저장
        )
        st.success(f"'{project_name}' 프로젝트의 문제정의서가 성공적으로 저장되었습니다.")
        # 관련 세션 상태 초기화
        del st.session_state['generated_problem_def']
        if 'problem_def_editor' in st.session_state:
            del st.session_state['problem_def_editor']
        st.rerun()

# --- 4. 저장된 문서 이력 ---
st.markdown("---")
st.subheader("📜 저장된 문제정의서 이력")
artifacts = get_artifacts_for_project(selected_id, "PROBLEM_DEF")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 문제정의서가 없습니다.")
