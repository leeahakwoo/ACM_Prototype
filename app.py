# your_mcp_project/app.py
# (오류 수정된 최종 대시보드 버전)

import streamlit as st

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(
    page_title="AI 개발 문서 자동화 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- session_state 초기화 --------------------
# 앱 실행 시 모든 문서의 데이터 구조를 초기화합니다.
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

# -------------------- 대시보드 UI --------------------
st.title("🚀 AI 개발 문서 자동화 대시보드")
st.markdown("---")

# --- 전체 진행률 계산 및 표시 ---
docs_list = [
    st.session_state.problem_definition,
    st.session_state.data_spec,
    st.session_state.model_spec,
    st.session_state.model_validation,
    st.session_state.trustworthy_validation
]
total_docs = len(docs_list)
completed_docs = sum(1 for doc in docs_list if any(doc.values()))
progress = completed_docs / total_docs if total_docs > 0 else 0

st.subheader("📊 전체 진행 상황")
st.progress(progress, text=f"{completed_docs} / {total_docs} 완료 ({progress:.0%})")
st.markdown("---")

# --- 상태 카드 생성을 위한 헬퍼 함수 (오류 수정된 부분) ---
def create_status_card(title, session_key, summary_key, page_path, icon):
    """문서 상태를 보여주는 카드를 생성하는 함수"""
    with st.container(border=True):
        st.subheader(f"{icon} {title}")
        
        # session_state에 해당 문서의 데이터가 있는지 확인
        # model_validation은 metrics가 채워져야 완료로 간주
        is_completed = any(st.session_state[session_key].get('validation_metrics', {})) if session_key == 'model_validation' else any(st.session_state[session_key].values())

        if is_completed:
            status_text = "✅ 작성 완료"
            summary_value = st.session_state[session_key].get(summary_key, "요약 정보 없음")
            st.success(status_text, icon="✅")
            # 내용이 길 경우 일부만 표시
            st.caption(f"**주요 내용:** {str(summary_value)[:40]}...")
        else:
            status_text = "❌ 작성 필요" # ★★★ 여기가 수정된 부분입니다.
            st.warning(status_text, icon="❌")
        
        # 해당 페이지로 바로 이동할 수 있는 링크 버튼 제공
        st.page_link(page_path, label=f"▶ {title} 페이지로 이동")

# --- 아키텍처에 따른 3단 컬럼 레이아웃 ---
plan_col, dev_col, val_col = st.columns(3)

with plan_col:
    st.header("1. 계획")
    create_status_card(
        "문제 정의서", "problem_definition", "project_name", 
        "pages/1_1_📝_문제_정의서.py", "📝"
    )

with dev_col:
    st.header("2. 개발")
    create_status_card(
        "데이터 정의서", "data_spec", "data_source",
        "pages/2_1_📈_데이터_정의서.py", "📈"
    )
    st.markdown("---")
    create_status_card(
        "모델 정의서", "model_spec", "model_name",
        "pages/2_2_🤖_모델_정의서.py", "🤖"
    )

with val_col:
    st.header("3. 검증")
    create_status_card(
        "성능 검증서", "model_validation", "summary",
        "pages/3_1_📊_성능_검증서.py", "📊"
    )
    st.markdown("---")
    create_status_card(
        "Trustworthy 검증서", "trustworthy_validation", "overall_summary",
        "pages/3_2_🛡️_Trustworthy_검증서.py", "🛡️"
    )

st.markdown("---")
st.info("👈 왼쪽 사이드바 또는 각 카드의 버튼을 클릭하여 문서를 작성하거나 수정할 수 있습니다.")
