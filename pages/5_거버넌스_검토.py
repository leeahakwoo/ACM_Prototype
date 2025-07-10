# pages/5_거버넌스_검토.py (콘텐츠 발전 모듈 적용 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
# gemini_agent에서 필요한 모든 함수를 import
from gemini_agent import generate_trustworthy_report, refine_content

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="거버넌스 검토", layout="wide")
st.title("🛡️ 거버넌스 검토: Trustworthy AI")
st.markdown("---")
st.info("""
AI 모델의 신뢰성을 확보하기 위해 **공정성, 설명가능성, 강건성**에 대한 검증 결과를 기록하고 종합적인 리스크를 분석합니다.
""")

# --- 1. 선택된 프로젝트 정보 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

problem_def_artifacts = get_artifacts_for_project(selected_id, "PROBLEM_DEF")
if not problem_def_artifacts:
    st.warning("이 프로젝트에 대한 '문제정의서'가 없습니다. 리스크 분석을 위해 '요구정의' 페이지에서 먼저 작성해주세요.")
    st.stop()
latest_problem_def = problem_def_artifacts[0]['content']

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")
with st.expander("참고: 이 프로젝트의 문제정의서 보기"):
    st.markdown(latest_problem_def)

# --- 2. 신뢰성 검증 결과 입력 ---
st.subheader("Step 1: 신뢰성 검증 결과 입력")
col1, col2, col3 = st.columns(3)
with col1:
    fairness_input = st.text_area("공정성(Fairness) 검증", height=150, help="예: 성별/연령 그룹 간 성능 지표 차이 분석...")
with col2:
    explainability_input = st.text_area("설명가능성(XAI) 검증", height=150, help="예: SHAP 분석 결과 주요 피처 영향도 확인...")
with col3:
    robustness_input = st.text_area("강건성(Robustness) 검증", height=150, help="예: Adversarial Attack 시뮬레이션 결과...")

# --- 3. AI 리포트 생성 ---
st.markdown("---")
if st.button("🤖 AI로 종합 리스크 분석 리포트 생성하기", type="primary", use_container_width=True):
    if not all([fairness_input, explainability_input, robustness_input]):
        st.error("모든 검증 결과 항목을 입력해야 리스크 분석을 할 수 있습니다.")
    else:
        with st.spinner("Gemini 에이전트가 신뢰성 리스크를 분석하고 리포트를 작성하고 있습니다..."):
            report_text = generate_trustworthy_report(
                latest_problem_def, fairness_input, explainability_input, robustness_input
            )
            st.session_state['generated_trust_report'] = report_text
            # 나중에 저장할 때를 대비해 원본 입력값도 저장
            st.session_state['trust_inputs'] = {
                'fairness': fairness_input,
                'explainability': explainability_input,
                'robustness': robustness_input
            }
            st.rerun()

# --- 4. 생성 결과 확인, 발전 및 저장 ---
if 'generated_trust_report' in st.session_state and st.session_state.get('generated_trust_report'):
    st.subheader("Step 2: 생성된 리포트 발전시키기")
    
    st.session_state['generated_trust_report'] = st.text_area(
        "내용을 검토하고 직접 수정하거나, 아래 AI 도구를 사용해 보세요.",
        value=st.session_state.generated_trust_report,
        height=400,
        key="trust_report_editor"
    )

    st.markdown("---")
    st.write("🤖 **AI 편집 도구모음**")
    current_text = st.session_state.trust_report_editor
    
    custom_instruction = st.text_input("직접 편집 지시하기 (예: 이 리포트를 EU AI Act 규제 관점에서 다시 검토해줘)")
    if st.button("실행", disabled=not custom_instruction, key="custom_trust_report"):
        with st.spinner("AI가 당신의 지시를 수행하고 있습니다..."):
            refined_text = refine_content(current_text, custom_instruction)
            st.session_state.generated_trust_report = refined_text
            st.rerun()

    st.markdown("---")
    st.subheader("Step 3: 최종본 저장")
    if st.button("💾 이 최종 리포트를 이력으로 저장하기", type="primary", use_container_width=True):
        trust_inputs = st.session_state.get('trust_inputs', {})
        full_content = (
            f"# Trustworthy AI 검증 리포트\n\n"
            f"## 공정성 검증\n{trust_inputs.get('fairness', 'N/A')}\n\n"
            f"## 설명가능성 검증\n{trust_inputs.get('explainability', 'N/A')}\n\n"
            f"## 강건성 검증\n{trust_inputs.get('robustness', 'N/A')}\n\n"
            f"---\n\n"
            f"## 종합 분석 및 제언\n{current_text}"
        )
        save_artifact(
            project_id=selected_id,
            stage="GOVERNANCE",
            type="TRUST_REPORT",
            content=full_content
        )
        st.success("Trustworthy AI 검증 리포트가 이력으로 저장되었습니다.")
        del st.session_state['generated_trust_report']
        del st.session_state['trust_inputs']
        st.rerun()

# --- 5. 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 Trustworthy AI 검증 리포트 이력")
artifacts = get_artifacts_for_project(selected_id, "TRUST_REPORT")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 Trustworthy AI 검증 리포트가 없습니다.")
