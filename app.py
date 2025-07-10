# your_mcp_project/app.py
# (최종 대시보드 버전)

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
# 이 작업은 대시보드 및 각 페이지의 안정적인 동작을 위해 필수적입니다.

# 1. 계획 단계
if 'problem_definition' not in st.session_state:
    st.session_state['
