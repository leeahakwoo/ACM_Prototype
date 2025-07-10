# pages/5_거버넌스_검토.py

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_trustworthy_report

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

# 해당 프로젝트의 최신 '문제정의서' 불러오기 (리스크 분석의 맥락으로 사용)
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

fairness_input = st.text_area(
    "**공정성 (Fairness)** 검증 결과",
    height=150,
    help="예: 성별, 연령 등 특정 인구 통계 그룹 간의 성능 지표(e.g., FPR, FNR) 차이를 분석한 결과, 통계적으로 유의미한 편향은 발견되지 않음 (Demographic Parity < 0.08)."
)

explainability_input = st.text_area(
    "**설명가능성 (Explainability, XAI)** 검증 결과",
    height=150,
    help="예: SHAP (SHapley Additive exPlanations) 분석 결과, '최근 6개월 구매액'과 '앱 체류 시간'이 모델 예측에 가장 큰 영향을 미치는 피처로 확인됨. 주요 피처의 영향도는 비즈니스 상식과 부합함."
)

robustness_input = st.text_area(
    "**강건성 (Robustness)** 검증 결과",
    height=150,
    help="예: Adversarial Attack 시뮬레이션 결과, 입력 데이터에 5%의 랜덤 노이즈를 주입했을 때 모델의 정확도(Accuracy) 하락률이 3% 이내로 안정적인 방어 능력을 보임."
)

# --- 3. AI 리포트 생성 및 저장 ---
st.markdown("---")
if st.button("🤖 AI로 종합 리스크 분석 리포트 생성하기", type="primary", use_container_width=True):
    if not all([fairness_input, explainability_input, robustness_input]):
        st.error("모든 검증 결과 항목을 입력해야 리스크 분석을 할 수 있습니다.")
    else:
        with st.spinner("Gemini 에이전트가 신뢰성 리스크를 분석하고 리포트를 작성하고 있습니다..."):
            report_text = generate_trustworthy_report(
                latest_problem_def,
                fairness_input,
                explainability_input,
                robustness_input
            )
            st.session_state['generated_trust_report'] = report_text

if 'generated_trust_report' in st.session_state:
    st.subheader("📝 생성된 Trustworthy AI 검증 리포트")
    final_text = st.text_area("내용을 검토하고 수정하세요.", value=st.session_state['generated_trust_report'], height=500)
    
    if st.button("💾 이 리포트를 이력으로 저장하기", use_container_width=True):
        full_content = f"# Trustworthy AI 검증 리포트\n\n## 공정성 검증\n{fairness_input}\n\n## 설명가능성 검증\n{explainability_input}\n\n## 강건성 검증\n{robustness_input}\n\n## 종합 분석 및 제언\n{final_text}"
        save_artifact(
            project_id=selected_id,
            stage="GOVERNANCE",
            type="TRUST_REPORT",
            content=full_content
        )
        st.success("Trustworthy AI 검증 리포트가 이력으로 저장되었습니다.")
        del st.session_state['generated_trust_report']
        st.rerun()

# --- 4. 저장된 이력 ---
st.markdown("---")
st.subheader("📜 저장된 Trustworthy AI 검증 리포트 이력")
artifacts = get_artifacts_for_project(selected_id, "TRUST_REPORT")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 Trustworthy AI 검증 리포트가 없습니다.")
