# pages/6_거버넌스_검토.py (AI 리포트 생성 기능 최종 연동)

import streamlit as st
import yaml
import re
import sys
import os
from datetime import datetime

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from persistence import get_latest_artifact, save_artifact, get_artifacts_for_project
from gemini_agent import generate_governance_summary

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
st.info("이전 단계들에서 저장된 모든 산출물을 자동으로 불러와 거버넌스 항목들을 점검합니다.")


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
        mcp_data = {} # 파싱 실패 시 빈 딕셔너리로 초기화
else:
    data_summary["MCP 컨텍스트"] = "❌ 없음"

problem_def_text = ""
if problem_def_artifact:
    data_summary["문제정의서"] = f"✅ (버전: {problem_def_artifact['created_at']})"
    problem_def_text = problem_def_artifact['content']
else:
    data_summary["문제정의서"] = "❌ 없음"

if design_doc_artifact:
    data_summary["모델 설계서"] = f"✅ (버전: {design_doc_artifact['created_at']})"
else:
    data_summary["모델 설계서"] = "❌ 없음"
    
perf_report_text = ""
if perf_report_artifact:
    data_summary["성능 검증 리포트"] = f"✅ (버전: {perf_report_artifact['created_at']})"
    perf_report_text = perf_report_artifact['content']
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
# 성능 리포트 텍스트에서 Accuracy 값을 정규식으로 추출
accuracy_match = re.search(r"Accuracy:\s*([0-9.]+)", perf_report_text)
accuracy = float(accuracy_match.group(1)) if accuracy_match else 0.0

# 규칙 기반 체크리스트
rules = {
    "담당자(responsible_party)가 MCP에 명시되었는가?": bool(responsible_party),
    "성능(Accuracy)이 0.9 이상인가?": accuracy >= 0.9,
    "고위험(High-Risk) 모델인가?": risk_level.lower() == "high",
    "개인정보 처리 관련 내용이 문제정의서에 포함되었는가?": "개인정보" in problem_def_text or "PII" in problem_def_text
}

passed_count = 0
check_results_text_list = []
for rule_name, is_passed in rules.items():
    if "고위험" in rule_name and is_passed:
        status_text = f"🟡 **주의:** {rule_name}"
        st.warning(status_text, icon="⚠️")
    elif is_passed:
        status_text = f"✅ **통과:** {rule_name}"
        st.success(status_text, icon="✔️")
        passed_count += 1
    else:
        status_text = f"❌ **미흡:** {rule_name}"
        st.error(status_text, icon="❗")
    check_results_text_list.append(status_text)


# --- 4. AI 기반 종합 리포트 생성 ---
st.markdown("---")
st.subheader("Step 3: AI 종합 리스크 분석")

if st.button("🤖 점검 결과 기반으로 리포트 생성", type="primary", use_container_width=True):
    with st.spinner("AI가 종합 리스크 분석 및 권고안을 작성합니다..."):
        report_text = generate_governance_summary(mcp_data, check_results_text_list)
        st.session_state['generated_gov_report'] = report_text
        st.rerun()

# --- 5. 생성된 리포트 확인 및 저장 ---
if 'generated_gov_report' in st.session_state and st.session_state.get('generated_gov_report'):
    st.subheader("📝 생성된 거버넌스 리포트")
    final_text = st.text_area(
        "AI가 생성한 리포트입니다. 내용을 검토하고 필요 시 수정하세요.",
        value=st.session_state.generated_gov_report,
        height=500,
        key="gov_report_editor"
    )
    
    if st.button("💾 이 리포트를 최종 저장하기", use_container_width=True):
        check_summary_str = "\n".join(check_results_text_list)
        full_content = f"# 종합 거버넌스 검토 리포트\n\n## 자동 점검 요약\n{check_summary_str}\n\n---\n\n## AI 종합 분석\n{final_text}"
        
        save_artifact(
            project_id=selected_id,
            stage="GOVERNANCE",
            type="GOV_REPORT",
            content=full_content
        )
        st.success("종합 거버넌스 리포트가 성공적으로 저장되었습니다.")
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
