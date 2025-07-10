# pages/2_설계.py (콘텐츠 발전 모듈 적용 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
# 'refine_content' 함수를 추가로 import 합니다.
from gemini_agent import generate_model_design_doc, refine_content

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="모델 설계", layout="wide")
st.title("🏗️ 모델 설계")
st.markdown("---")

# --- 1. 선택된 프로젝트 정보 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

problem_def_artifacts = get_artifacts_for_project(selected_id, "PROBLEM_DEF")
if not problem_def_artifacts:
    st.warning("이 프로젝트에 대한 '문제정의서'가 없습니다. '요구정의' 페이지에서 먼저 작성해주세요.")
    st.stop()
latest_problem_def = problem_def_artifacts[0]['content']

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")
with st.expander("참고: 이 프로젝트의 문제정의서 보기"):
    st.markdown(latest_problem_def)

# --- 2. 모델 설계서 생성기 ---
st.subheader("Step 1: 모델 설계서 생성")
model_type = st.selectbox(
    "설계할 모델의 주요 유형을 선택하세요.",
    ("텍스트 분류", "이미지 분류", "회귀", "객체 탐지", "자연어 생성", "기타")
)
if st.button("🤖 AI로 모델 설계서 초안 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 문제정의서 기반으로 모델 설계를 하고 있습니다..."):
        generated_text = generate_model_design_doc(latest_problem_def, model_type)
        st.session_state['generated_design_doc'] = generated_text
        st.rerun()

# --- 3. 생성 결과 확인, 발전 및 저장 (핵심 수정 부분) ---
if 'generated_design_doc' in st.session_state and st.session_state.get('generated_design_doc'):
    st.subheader("Step 2: 생성된 초안 발전시키기")
    
    st.session_state['generated_design_doc'] = st.text_area(
        "내용을 검토하고 직접 수정하거나, 아래 AI 도구를 사용해 보세요.", 
        value=st.session_state.generated_design_doc, 
        height=400,
        key="design_doc_editor"
    )

    st.markdown("---")
    st.write("🤖 **AI 편집 도구모음**")

    col1, col2, col3 = st.columns(3)
    current_text = st.session_state.design_doc_editor

    with col1:
        if st.button("✨ 전문가처럼 다듬기", use_container_width=True, key="refine_design"):
            with st.spinner("AI가 문체를 다듬고 있습니다..."):
                instruction = "이 모델 설계서의 내용을 더 논리 정연하고 기술적으로 상세하게 다듬어줘."
                refined_text = refine_content(current_text, instruction)
                st.session_state.generated_design_doc = refined_text
                st.rerun()

    with col2:
        if st.button("🤏 간결하게 요약하기", use_container_width=True, key="summarize_design"):
            with st.spinner("AI가 내용을 요약하고 있습니다..."):
                instruction = "이 설계서의 핵심 내용을 경영진 보고용으로 3문장으로 요약해줘."
                refined_text = refine_content(current_text, instruction)
                st.session_state.generated_design_doc = refined_text
                st.rerun()

    with col3:
        if st.button("❓ 질문으로 확인하기", use_container_width=True, key="question_design"):
            with st.spinner("AI가 설계의 잠재적 이슈를 질문으로 만들고 있습니다..."):
                instruction = "이 모델 설계 내용에서 발생할 수 있는 잠재적인 기술적 리스크나 논리적 허점을 질문 형태로 3가지 제시해줘."
                refined_text = refine_content(current_text, instruction)
                # 질문은 기존 내용에 덧붙여서 보여줌
                st.session_state.generated_design_doc = current_text + "\n\n---\n\n### AI의 검토 질문:\n" + refined_text
                st.rerun()

    custom_instruction = st.text_input("직접 편집 지시하기 (예: 이 설계에 대한 대안으로 CNN 모델을 간략히 추가해줘)")
    if st.button("실행", disabled=not custom_instruction, key="custom_design"):
        with st.spinner("AI가 당신의 지시를 수행하고 있습니다..."):
            refined_text = refine_content(current_text, custom_instruction)
            st.session_state.generated_design_doc = refined_text
            st.rerun()

    st.markdown("---")
    st.subheader("Step 3: 최종본 저장")
    if st.button("💾 이 최종본을 데이터베이스에 저장하기", type="primary", use_container_width=True):
        save_artifact(
            project_id=selected_id,
            stage="DESIGN",
            type="MODEL_DESIGN",
            content=current_text
        )
        st.success("모델 설계서가 성공적으로 저장되었습니다.")
        del st.session_state['generated_design_doc']
        if 'design_doc_editor' in st.session_state:
            del st.session_state.design_doc_editor
        st.rerun()

# --- 4. 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 모델 설계서 이력")
artifacts = get_artifacts_for_project(selected_id, "MODEL_DESIGN")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 모델 설계서가 없습니다.")
