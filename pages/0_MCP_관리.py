# pages/0_MCP_관리.py (신규 파일)

import streamlit as st
import yaml  # YAML 처리를 위한 라이브러리
import os
from datetime import datetime

# --- (경로 설정 및 persistence import) ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from persistence import save_artifact, get_artifacts_for_project

st.title("Ⓜ️ MCP (Model Context Protocol) 관리")
st.markdown("---")

selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("프로젝트를 선택해주세요.")
    st.stop()

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")

# --- MCP YAML 생성기 ---
st.subheader("Step 1 & 2: MCP YAML 생성 및 저장")

# MCP 템플릿 정의
mcp_template = {
    'mcp_context': {
        'model_id': f"PROJ_{selected_id}_{datetime.now().strftime('%Y%m%d')}",
        'use_case': "예: 고객 민원 자동 분류",
        'data_source': "예: 내부 CRM 데이터베이스",
        'risk_level': "Medium",
        'performance': {'accuracy': 0.0, 'f1_score': 0.0},
        'responsible_party': "AI 개발팀",
        'last_modified': datetime.now().isoformat()
    }
}

# st.text_area를 사용하여 사용자가 YAML을 직접 편집하도록 함
yaml_str = st.text_area(
    "모델의 메타정보를 YAML 형식으로 입력 또는 수정하세요.",
    value=yaml.dump(mcp_template, allow_unicode=True, sort_keys=False),
    height=300
)

if st.button("💾 MCP YAML 저장하기", type="primary"):
    try:
        # 입력된 문자열이 유효한 YAML인지 검증
        parsed_yaml = yaml.safe_load(yaml_str)
        
        # 유효하다면 파일로 저장하고, 그 내용을 DB에도 기록
        file_name = f"mcp_{parsed_yaml['mcp_context']['model_id']}.yaml"
        
        # (실제 환경에서는 /artifacts 와 같은 영구 저장소 경로를 사용해야 함)
        # 프로토타입에서는 프로젝트 루트에 저장
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(yaml_str)

        # DB에는 파일 경로와 함께 YAML 내용 자체도 저장
        save_artifact(
            project_id=selected_id,
            stage="MCP",
            type="MCP_YAML",
            content=yaml_str
        )
        st.session_state['last_mcp_file'] = file_name # 파일 경로를 세션에 저장
        st.success(f"MCP 파일 '{file_name}' 이(가) 성공적으로 저장되었습니다.")

    except yaml.YAMLError as e:
        st.error(f"YAML 형식 오류: {e}")
