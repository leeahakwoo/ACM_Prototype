# pages/0_MCP_관리.py

import streamlit as st
import yaml
import os
from datetime import datetime
import sys

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project

st.set_page_config(page_title="MCP 관리", layout="wide")
st.title("Ⓜ️ MCP (Model Context Protocol) 관리")
st.markdown("---")

# --- 프로젝트 선택 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("프로젝트를 선택해주세요. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")

# --- MCP YAML 생성기 ---
st.subheader("MCP YAML 생성 및 저장")
st.info("모델의 주요 메타정보를 YAML 형식으로 작성하여 버전 관리합니다. 이 정보는 '거버넌스 검토' 단계에서 자동으로 사용됩니다.")

# MCP 템플릿 정의
mcp_template = {
    'mcp_context': {
        'model_id': f"PROJ_{selected_id}_{datetime.now().strftime('%Y%m%d%H%M')}",
        'model_name': st.session_state.get('selected_project_name', 'N/A'),
        'version_tag': 'v1.0.0',
        'use_case': "예: 고객 민원 자동 분류",
        'data_source': "예: 내부 CRM 데이터베이스 2024년 로그",
        'risk_level': "Medium",
        'status': 'Development',
        'performance': {'accuracy': 0.0, 'f1_score': 0.0},
        'responsible_party': "AI 개발팀",
        'last_modified': datetime.now().isoformat()
    }
}

# st.text_area를 사용하여 사용자가 YAML을 직접 편집하도록 함
yaml_str = st.text_area(
    "모델의 메타정보를 YAML 형식으로 입력 또는 수정하세요.",
    value=yaml.dump(mcp_template, allow_unicode=True, sort_keys=False, indent=2),
    height=400
)

if st.button("💾 MCP YAML 저장하기", type="primary", use_container_width=True):
    try:
        parsed_yaml = yaml.safe_load(yaml_str)
        if 'mcp_context' not in parsed_yaml or 'model_id' not in parsed_yaml['mcp_context']:
             st.error("YAML 내용에 'mcp_context'와 'model_id' 키가 반드시 포함되어야 합니다.")
        else:
            # DB에는 YAML 내용 자체를 저장
            save_artifact(
                project_id=selected_id,
                stage="MCP",
                type="MCP_YAML",
                content=yaml_str
            )
            st.success(f"MCP 정보가 성공적으로 저장되었습니다.")
            st.rerun()

    except yaml.YAMLError as e:
        st.error(f"YAML 형식 오류가 발생했습니다. 내용을 다시 확인해주세요: {e}")


# --- 저장된 MCP 이력 ---
st.markdown("---")
st.header("📜 저장된 MCP 이력")
artifacts = get_artifacts_for_project(selected_id, "MCP_YAML")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.code(artifact['content'], language='yaml')
else:
    st.info("이 프로젝트에 저장된 MCP 파일이 없습니다.")
