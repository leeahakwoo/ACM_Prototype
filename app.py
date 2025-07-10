# your_mcp_project/app.py

import streamlit as st

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(
    page_title="AI 개발 문서 자동화 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- session_state 초기화 (모든 페이지의 데이터 구조를 여기서 정의) --------------------
# 이것이 앱의 '단일 진실 공급원(Single Source of Truth)' 역할을 합니다.
states_to_initialize = {
    'problem_definition': {
        "project_name": "", "project_goal": "", "problem_background": "", "expected_output": ""
    },
    'data_spec': {
        "data_source": "", "data_schema": "", "preprocessing_steps": "", "privacy_issues": ""
    },
    'model_spec': {
        "model_name": "", "model_type": "분류", "key_features": "", "hyperparameters": ""
    },
    'model_validation': {
        "validation_metrics": {}, "summary": ""
    },
    'trustworthy_validation': {
        "fairness_result": "", "explainability_result": "", "robustness_result": "", "overall_summary": ""
    }
}
for key, value in states_to_initialize.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- 헬퍼 함수 status_card(title, session_key, summary_key, page_path, icon):
    """문서 상태를 보여주는 카드를 생성하는 함수"""
    with st.container(border=True):
        st.subheader(f"{icon} {title}")
        
        # session_state에 해당 문서의 데이터가 있는지 확인
        if any(st.session_state[session_key].values()):
            status_text = "✅ 작성 완료"
            summary_value = st.session_state[session_key].get(summary_key, "요약 정보 없음")
            st.success(status_text, icon="✅")
            st.caption(f"**주요 내용:** {summary_value}")
        else:
            status_text = "--------------------
def get_status(data_dict: dict) -> str:
    """세션 상태 딕셔너리를 확인하여 완료 여부를 반환하는 함수"""
    # 딕셔너리의 값 중 하나라도 채워져 있으면 완료로 간주 (단순한 기준)
    # model_validation은 metrics가 채워져야 완료로 간주
    if 'validation_metrics' in data_dict:
        return "작성 완료 ✅" if data_dict['validation_metrics'] else "작성 필요 ❌"
    
    return "작성 완료 ✅" if any(data_dict.values()) else "작성 필요 ❌"

def check_all_complete() -> bool:
    """모든 문서가 작성되었는지 확인하는 함수"""
    statuses = [
        get_status(st.session_state.problem_definition),
        get_status(st.session_❌ 작성 필요"
            st.warning(status_text, icon="❌")
        
        # 해당state.data_spec),
        get_status(st.session_state.model_spec),
         페이지로 바로 이동할 수 있는 링크 버튼 제공
        st.page_link(page_path, label=f"▶get_status(st.session_state.model_validation),
        get_status(st.session_state.trustworthy_validation)
    ]
    return all(status == "작성 완료 ✅" for status in {title} 페이지로 이동")


# --- 아키텍처에 따른 3단 컬럼 레이아웃 ---
plan_col, dev_col, val_col = st.columns(3)

with plan_col: statuses)

# -------------------- 대시보드 UI --------------------

st.title("🚀 AI 개발 문서
    st.header("1. 계획")
    create_status_card(
        "문제 정의서", " 자동화 대시보드")
st.header(st.session_state.problem_definition.get('problem_definition", "project_name", 
        "pages/1_1_📝_문제_정의서project_name') or "새 프로젝트")
st.markdown("---")

st.info("👈 왼쪽 사이드바.py", "📝"
    )

with dev_col:
    st.header("2. 개발")
    create_status_card(
        "데이터 정의서", "data_spec", "data_source에서 각 문서를 작성하고 현황을 여기서 확인하세요.", icon="ℹ️")

# 3단 컬럼으로",
        "pages/2_1_📈_데이터_정의서.py", "📈"
    ) 레이아웃 구성
col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("---") # 구분선
    create_status_card(
        "모델 정의서", "    st.subheader("1. 계획 (Planning)")
    with st.container(border=True):
        stmodel_spec", "model_name",
        "pages/2_2_🤖_모델_정의.markdown(f"**- 문제 정의서:** {get_status(st.session_state.problem_definition)}")
서.py", "🤖"
    )

with val_col:
    st.header("3.        st.caption(f"목표: {st.session_state.problem_definition.get('project 검증")
    create_status_card(
        "성능 검증서", "model_validation", "_goal', '미작성')[:30]}...")

with col2:
    st.subheader("2.summary",
        "pages/3_1_📊_성능_검증서.py", "📊 개발 (Development)")
    with st.container(border=True):
        st.markdown(f"**"
    )
    st.markdown("---") # 구분선
    create_status_card(
- 데이터 정의서:** {get_status(st.session_state.data_spec)}")
        st.caption        "Trustworthy 검증서", "trustworthy_validation", "overall_summary",
        "pages/(f"출처: {st.session_state.data_spec.get('data_source', '3_2_🛡️_Trustworthy_검증서.py", "🛡️"
    )

미작성')[:30]}...")
        st.markdown(f"**- 모델 정의서:** {getst.markdown("---")
st.info("👈 왼쪽 사이드바 또는 각 카드의 버튼을 클릭하여 문_status(st.session_state.model_spec)}")
        st.caption(f"모델명: {st.서를 작성하거나 수정할 수 있습니다.")
