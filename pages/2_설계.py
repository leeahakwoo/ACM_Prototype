# pages/2_설계.py

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_model_design_doc

st.set_page_config(page_title="모델 설계", layout="wide")
st.title("🏗️ 모델 설계")
st.markdown("---")

# --- 1. 선택된 프로젝트 정보 확인 ---
selected_id = st.session_state.get('selected_project_id', None)

if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

# 해당 프로젝트의 최신 '문제정의서' 불러오기
problem_def_artifacts = get_artifacts_for_project(selected_id, "PROBLEM_DEF")

if not problem_def_artifacts:
    st.warning("이 프로젝트에 대한 '문제정의서'가 없습니다. '요구정의' 페이지에서 먼저 작성해주세요.")
    st.stop()

# 가장 최신 버전의 문제정의서 사용
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

# --- 3. 생성 결과 확인 및 저장 ---
if 'generated_design_doc' in st.session_state and st.session_state['generated_design_doc']:
    st.subheader("📝 생성된 모델 설계서 초안")
    
    final_text = st.text_area("내용을 검토하고 수정하세요.", value=st.session_state.generated_design_doc, height=500)
    
    if st.button("💾 데이터베이스에 저장하기", use_container_width=True):
        save_artifact(
            project_id=selected_id,
            stage="DESIGN",
            type="MODEL_DESIGN",
            content=final_text
        )
        st.success("모델 설계서가 성공적으로 저장되었습니다.")
        del st.session_state['generated_design_doc']
        st.rerun()

# --- 4. 저장된 문서 이력 ---
st.markdown("---")
st.subheader("📜 저장된 모델 설계서 이력")
artifacts = get_artifacts_for_project(selected_id, "MODEL_DESIGN")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 모델 설계서가 없습니다.")
