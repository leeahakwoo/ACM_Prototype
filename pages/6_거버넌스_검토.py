# pages/6_거버넌스_검토.py

import streamlit as st
from datetime import datetime
import sys
import os
import yaml

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_trustworthy_report, refine_content

# --- 페이지 설정 ---
st.set_page_config(page_title="거버넌스 검증", layout="wide")

# --- 페이지 제목 ---
st.title("🛡️ 거버넌스 검증")
st.markdown("---")
st.info("MCP YAML 파일을 기반으로 모델의 신뢰성을 점검하고, 종합적인 리스크 분석 리포트를 생성합니다.")

# --- 프로젝트 선택 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("프로젝트를 선택해주세요. 메인 대시보드(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()
st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")

# --- MCP YAML 파일 불러오기 ---
st.subheader("Step 1: 점검 대상 MCP YAML 불러오기")
mcp_artifacts = get_artifacts_for_project(selected_id, "MCP_YAML")
if not mcp_artifacts:
    st.warning("이 프로젝트에 대한 MCP YAML 파일이 없습니다. '거버넌스 관리' 페이지에서 먼저 생성해주세요.")
    st.stop()
mcp_versions = {f"{artifact['created_at']} 버전": artifact['content'] for artifact in mcp_artifacts}
selected_version_key = st.selectbox("점검할 MCP 버전을 선택하세요.", options=list(mcp_versions.keys()))
latest_mcp_yaml_str = mcp_versions[selected_version_key]
try:
    mcp_data = yaml.safe_load(latest_mcp_yaml_str).get('mcp_context', {})
except (yaml.YAMLError, AttributeError):
    st.error("선택된 MCP YAML 파일의 형식이 잘못되었습니다."); st.stop()
with st.expander("로드된 MCP 컨텍스트 전문 보기"):
    st.json(mcp_data)

# --- 거버넌스 기준 자동 점검 ---
st.subheader("Step 2: 거버넌스 기준 자동 점검 결과")
high_risk_checklist = {
    "책임자(responsible_party) 명시 여부": "responsible_party" in mcp_data and mcp_data["responsible_party"],
    "성능 지표(performance) 정의 여부": "performance" in mcp_data and mcp_data["performance"],
}
risk_level = mcp_data.get('risk_level', 'Unknown')
st.metric("모델 리스크 등급 (Risk Level)", risk_level)
check_results = []
if risk_level.lower() == "high":
    st.write("**고위험(High-Risk) 모델에 대한 필수 점검 결과:**")
    all_passed = True
    for item, passed in high_risk_checklist.items():
        result_text = f"✅ **충족:** {item}" if passed else f"❌ **미충족:** {item}"
        if passed: st.success(result_text, icon="✅")
        else: st.error(result_text, icon="🚨"); all_passed = False
        check_results.append(result_text)
    if not all_passed: st.warning("**보완 가이드:** '거버넌스 관리' 페이지에서 YAML 파일의 미충족 항목을 보완해주세요.")
else:
    st.info(f"현재 모델은 '{risk_level}' 등급으로 분류되어, 고위험 모델에 대한 필수 점검 대상이 아닙니다.")

# --- AI 리포트 생성 ---
st.markdown("---")
st.subheader("Step 3: AI 종합 리스크 분석 리포트")
if st.button("🤖 AI로 종합 리스크 분석 리포트 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 자동 점검 결과를 바탕으로 리스크를 분석하고 있습니다..."):
        # (이전과 동일한 로직)
        report_text = ... # generate_trustworthy_report 호출
        st.session_state['generated_gov_report'] = report_text
        st.rerun()

# --- 생성 결과 확인, 발전 및 저장 ---
if 'generated_gov_report' in st.session_state:
    st.subheader("Step 4: 생성된 리포트 발전시키기 및 저장")
    # ... (AI 편집 도구모음 및 저장 로직 추가)

# --- 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 거버넌스 검토 리포트 이력")
artifacts = get_artifacts_for_project(selected_id, "GOV_REPORT")
# (이하 이력 표시 로직)
