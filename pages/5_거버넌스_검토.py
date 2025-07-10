# pages/5_거버넌스_검토.py (MCP YAML 연동 버전)

import streamlit as st
from datetime import datetime
import sys
import os
import yaml

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_trustworthy_report  # 이 함수는 재사용 및 수정될 예정

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="거버넌스 검토", layout="wide")
st.title("🛡️ 거버넌스 검토 (MCP 연동)")
st.markdown("---")

# --- 1. 선택된 프로젝트 정보 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")

# --- 2. MCP YAML 파일 불러오기 ---
st.subheader("Step 1: 점검 대상 MCP YAML 불러오기")

mcp_artifacts = get_artifacts_for_project(selected_id, "MCP_YAML")

if not mcp_artifacts:
    st.warning("이 프로젝트에 대한 MCP YAML 파일이 없습니다. 'MCP 관리' 페이지에서 먼저 생성해주세요.")
    st.stop()

# 여러 버전의 MCP 파일 중 선택 가능하도록 UI 구성
mcp_versions = {f"{artifact['created_at']} 버전": artifact['content'] for artifact in mcp_artifacts}
selected_version_key = st.selectbox("점검할 MCP 버전을 선택하세요.", options=list(mcp_versions.keys()))

latest_mcp_yaml_str = mcp_versions[selected_version_key]

try:
    mcp_data = yaml.safe_load(latest_mcp_yaml_str).get('mcp_context', {})
except (yaml.YAMLError, AttributeError):
    st.error("선택된 MCP YAML 파일의 형식이 잘못되었습니다.")
    st.stop()

with st.expander("로드된 MCP 컨텍스트 전문 보기"):
    st.json(mcp_data)

# --- 3. 거버넌스 기준 자동 점검 ---
st.subheader("Step 2: 거버넌스 기준 자동 점검 결과")

# 예시: 리스크 레벨에 따른 체크리스트
high_risk_checklist = {
    "책임자(responsible_party) 명시 여부": "responsible_party" in mcp_data and mcp_data["responsible_party"],
    "성능 지표(performance) 정의 여부": "performance" in mcp_data and mcp_data["performance"],
    "데이터 출처(data_source) 명시 여부": "data_source" in mcp_data and mcp_data["data_source"],
    "사용 사례(use_case) 명시 여부": "use_case" in mcp_data and mcp_data["use_case"],
}

risk_level = mcp_data.get('risk_level', 'Unknown')
st.metric("모델 리스크 등급 (Risk Level)", risk_level)

check_results = []
if risk_level.lower() == "high":
    st.write("**고위험(High-Risk) 모델에 대한 필수 점검 결과:**")
    all_passed = True
    for item, passed in high_risk_checklist.items():
        if passed:
            result_text = f"✅ **충족:** {item}"
            st.success(result_text, icon="✅")
        else:
            result_text = f"❌ **미충족:** {item}"
            st.error(result_text, icon="🚨")
            all_passed = False
        check_results.append(result_text)
    
    if not all_passed:
        st.warning("**보완 가이드:** 'MCP 관리' 페이지로 돌아가 YAML 파일에 누락된 필수 항목을 모두 기입한 후, 새 버전으로 저장해주세요.")
else:
    st.info(f"현재 모델은 '{risk_level}' 등급으로 분류되어, 고위험 모델에 대한 필수 점검 대상이 아닙니다.")
    check_results.append(f"'{risk_level}' 등급으로 고위험 모델 필수 점검 대상이 아님.")


# --- 4. AI 기반 종합 리스크 분석 ---
st.markdown("---")
st.subheader("Step 3: AI 종합 리스크 분석 리포트")

if st.button("🤖 AI로 종합 리스크 분석 리포트 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 자동 점검 결과를 바탕으로 리스크를 분석하고 있습니다..."):
        # gemini_agent의 함수를 재활용. 입력을 조금 다르게 구성
        # problem_def 대신 로드된 mcp yaml 전체를 전달
        # fairness, explainability, robustness 입력 대신 자동 점검 결과를 전달
        check_result_str = "\n".join(check_results)
        
        # generate_trustworthy_report 함수를 호출하기 위해 입력 형식 맞춤
        # 실제로는 이 프롬프트를 사용하는 새로운 agent 함수를 만드는 것이 더 좋음
        report_text = generate_trustworthy_report(
            problem_def=yaml.dump(mcp_data, allow_unicode=True),
            fairness_input=f"점검 결과: {risk_level} 등급",
            explainability_input=f"주요 항목 점검 결과:\n{check_result_str}",
            robustness_input="수동 검토 필요"
        )
        st.session_state['generated_gov_report'] = report_text
        st.rerun()

# --- 5. 생성된 리포트 확인 및 저장 ---
if 'generated_gov_report' in st.session_state:
    st.subheader("📝 생성된 리스크 분석 리포트")
    final_text = st.text_area("내용을 검토하고 수정하세요.", value=st.session_state.generated_gov_report, height=400)
    
    if st.button("💾 이 리포트를 이력으로 저장하기", use_container_width=True):
        save_artifact(
            project_id=selected_id,
            stage="GOVERNANCE",
            type="GOV_REPORT",
            content=final_text
        )
        st.success("거버넌스 검토 리포트가 이력으로 저장되었습니다.")
        del st.session_state['generated_gov_report']
        st.rerun()

# --- 6. 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 거버넌스 검토 리포트 이력")
artifacts = get_artifacts_for_project(selected_id, "GOV_REPORT")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 거버넌스 검토 리포트가 없습니다.")
