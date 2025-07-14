# pages/6_거버넌스_검토.py (자동 검증 기능 추가)

import streamlit as st
import re
import yaml
# ... (기타 import)

st.title("🛡️ 거버넌스 검증 (자동화)")
st.markdown("---")

# --- 1. 데이터 수집 및 컨텍스트 추출 ---
selected_id = st.session_state.get('selected_project_id')
if not selected_id:
    # ... 프로젝트 선택 유도 ...
    st.stop()

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")

with st.spinner("프로젝트의 모든 산출물을 불러와 분석 중입니다..."):
    # DB에서 모든 종류의 최신 산출물을 가져오는 함수 (persistence.py에 구현 필요)
    # get_latest_artifacts_for_project(selected_id)
    artifacts = {
        "MCP_YAML": get_artifacts_for_project(selected_id, "MCP_YAML"),
        "PROBLEM_DEF": get_artifacts_for_project(selected_id, "PROBLEM_DEF"),
        "MODEL_DESIGN": get_artifacts_for_project(selected_id, "MODEL_DESIGN"),
        "PERF_REPORT": get_artifacts_for_project(selected_id, "PERF_REPORT"),
    }
    
    # 각 산출물에서 정보 추출
    mcp_data = {}
    if artifacts["MCP_YAML"]:
        mcp_data = yaml.safe_load(artifacts["MCP_YAML"][0]['content']).get('mcp_context', {})
    
    problem_def_text = artifacts["PROBLEM_DEF"][0]['content'] if artifacts["PROBLEM_DEF"] else ""
    perf_report_text = artifacts["PERF_REPORT"][0]['content'] if artifacts["PERF_REPORT"] else ""

    # 예시: 성능 리포트에서 Accuracy 추출
    accuracy_match = re.search(r"Accuracy:\s*([0-9.]+)", perf_report_text)
    accuracy = float(accuracy_match.group(1)) if accuracy_match else None


# --- 2. 자동 점검 수행 및 결과 표시 ---
st.subheader("자동 거버넌스 점검 결과")

# Rule-based Checklist
rules = {
    "담당자 지정 여부": bool(mcp_data.get("responsible_party")),
    "고위험 모델 여부": mcp_data.get("risk_level", "").lower() == "high",
    "성능 목표 달성 여부 (Accuracy > 0.9)": accuracy is not None and accuracy > 0.9,
    "개인정보 포함 가능성": "개인정보" in problem_def_text
}

passed_count = 0
failed_count = 0
for rule_name, is_passed in rules.items():
    # 조건에 따라 통과/실패/주의 표시
    if rule_name == "고위험 모델 여부" and is_passed:
        st.warning(f"🟡 **주의:** {rule_name} (고위험 모델로 분류됨)", icon="⚠️")
    elif is_passed:
        st.success(f"✅ **통과:** {rule_name}", icon="✔️")
        passed_count += 1
    else:
        st.error(f"❌ **미흡:** {rule_name}", icon="❗")
        failed_count += 1

st.metric("점검 결과", f"{passed_count} / {len(rules)} 충족")


# --- 3. AI 기반 종합 리포트 생성 ---
st.markdown("---")
st.subheader("AI 종합 리스크 분석 리포트")

# 점검 결과를 텍스트로 변환하여 AI 프롬프트에 전달
summary_of_checks = "\n".join([f"- {name}: {'충족' if passed else '미흡'}" for name, passed in rules.items()])

if st.button("🤖 점검 결과 기반으로 리포트 생성", type="primary"):
    with st.spinner("AI가 종합 리스크 분석 및 권고안을 작성합니다..."):
        # 여기에 점검 결과를 바탕으로 리포트를 생성하는 gemini_agent 함수 호출
        # 예: generate_governance_summary(summary_of_checks, mcp_data)
        report_text = ... 
        st.markdown(report_text)
