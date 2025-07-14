# pages/6_거버넌스_검증.py (데이터 집계 및 자동 점검 1단계)

import streamlit as st
import yaml
import re
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from persistence import get_latest_artifact
# (향후 AI 리포트 생성을 위해 gemini_agent도 추가 예정)
# from gemini_agent import ...

# --- 페이지 설정 ---
st.set_page_config(page_title="거버넌스 검증", layout="wide")
st.title("🛡️ 거버넌스 검증 (자동화)")
st.markdown("---")

# --- 1. 프로젝트 선택 확인 ---
selected_id = st.session_state.get('selected_project_id')
if not selected_id:
    st.error("프로젝트를 선택해주세요. 메인 대시보드(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()
st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")

# --- 2. 데이터 집계 및 컨텍스트 추출 ---
st.subheader("Step 1: 프로젝트 데이터 자동 집계")

# 각 산출물의 최신 버전을 불러옵니다.
with st.spinner("프로젝트의 모든 산출물 데이터를 불러오는 중입니다..."):
    mcp_artifact = get_latest_artifact(selected_id, "MCP_YAML")
    problem_def_artifact = get_latest_artifact(selected_id, "PROBLEM_DEF")
    design_doc_artifact = get_latest_artifact(selected_id, "MODEL_DESIGN")
    perf_report_artifact = get_latest_artifact(selected_id, "PERF_REPORT")

# 각 산출물의 존재 여부 확인 및 컨텍스트 추출
data_summary = {}
mcp_data = {}
if mcp_artifact:
    data_summary["MCP 컨텍스트"] = f"✅ (버전: {mcp_artifact['created_at']})"
    try:
        mcp_data = yaml.safe_load(mcp_artifact['content']).get('mcp_context', {})
    except (yaml.YAMLError, AttributeError):
        st.error("MCP YAML 파일 파싱에 실패했습니다.")
else:
    data_summary["MCP 컨텍스트"] = "❌ 없음"

if problem_def_artifact:
    data_summary["문제정의서"] = f"✅ (버전: {problem_def_artifact['created_at']})"
else:
    data_summary["문제정의서"] = "❌ 없음"

if design_doc_artifact:
    data_summary["모델 설계서"] = f"✅ (버전: {design_doc_artifact['created_at']})"
else:
    data_summary["모델 설계서"] = "❌ 없음"
    
if perf_report_artifact:
    data_summary["성능 검증 리포트"] = f"✅ (버전: {perf_report_artifact['created_at']})"
else:
    data_summary["성능 검증 리포트"] = "❌ 없음"

# 집계된 데이터 현황 표시
st.table(data_summary)

# 모든 필수 데이터가 있는지 확인
if not all([mcp_artifact, problem_def_artifact, design_doc_artifact, perf_report_artifact]):
    st.error("거버넌스 검증을 수행하기 위해 필요한 모든 산출물이 준비되지 않았습니다. 각 페이지에서 문서를 먼저 작성 및 저장해주세요.")
    st.stop()

# --- 3. 자동 점검 수행 ---
st.markdown("---")
st.subheader("Step 2: 자동 거버넌스 점검 결과")

# 컨텍스트에서 점검에 필요한 값 추출
risk_level = mcp_data.get("risk_level", "Unknown")
responsible_party = mcp_data.get("responsible_party", "")
performance_metrics = mcp_data.get("performance", {})
accuracy = performance_metrics.get("accuracy", 0.0)

# 규칙 기반 체크리스트
rules = {
    "담당자(responsible_party)가 MCP에 명시되었는가?": bool(responsible_party),
    "성능(Accuracy)이 0.9 이상인가?": accuracy >= 0.9,
    "고위험(High-Risk) 모델인가?": risk_level.lower() == "high",
}

passed_count = 0
for rule_name, is_passed in rules.items():
    if "고위험" in rule_name and is_passed:
        st.warning(f"🟡 **주의:** {rule_name}", icon="⚠️")
    elif is_passed:
        st.success(f"✅ **통과:** {rule_name}", icon="✔️")
        passed_count += 1
    else:
        st.error(f"❌ **미흡:** {rule_name}", icon="❗")

st.metric("필수 점검 항목 충족률", f"{passed_count} / {len(rules) - 1}") # '고위험' 항목은 평가에서 제외

# --- 4. AI 기반 종합 리포트 (다음 단계에서 구현) ---
st.markdown("---")
st.subheader("Step 3: AI 종합 리스크 분석")
st.info("다음 단계에서는 이 자동 점검 결과를 바탕으로 AI가 종합적인 리스크 분석 및 권고안을 생성하는 기능을 구현합니다.")
