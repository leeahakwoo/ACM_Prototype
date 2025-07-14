# app.py (st.Page를 이용한 메뉴 커스터마이징 최종 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

# --- 페이지 정의 (st.Page 사용) ---
# 이것이 사이드바 메뉴를 완전히 제어하는 핵심 부분입니다.
pg = st.navigation(
    [
        st.Page("app.py", title="대시보드", icon="🚀"),
        st.Page("pages/1_거버넌스_관리.py", title="거버넌스 관리", icon="Ⓜ️"),
        st.Page("pages/2_문제정의.py", title="문제정의", icon="📋"),
        st.Page("pages/3_모델_설계.py", title="모델 설계", icon="🏗️"),
        st.Page("pages/4_모델_구현.py", title="모델 구현", icon="⚙️"),
        st.Page("pages/5_성능_검증.py", title="성능 검증", icon="📊"),
        st.Page("pages/6_거버넌스_검증.py", title="거버넌스 검증", icon="🛡️"),
    ]
)

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 관리 지원 도구",
    page_icon="🚀",
    layout="wide",
)

# --- 선택된 페이지 실행 ---
pg.run()

# --- 이하 코드는 pg.is_active 와 pg.title 을 사용하여 현재 페이지를 확인합니다.
# 이 코드는 app.py가 실행될 때만 (즉, 대시보드 페이지에서만) 보이게 됩니다.
if pg.title == "대시보드":
    
    # --- 타이틀 ---
    st.title("🚀 AI 관리 지원 도구")
    st.markdown("---")

    # --- session_state 관리 ---
    if 'editing_project_id' not in st.session_state:
        st.session_state.editing_project_id = None
    if 'selected_project_id' not in st.session_state:
        st.session_state.selected_project_id = None

    # --- 사이드바: 프로젝트 생성/수정 ---
    # (이전 답변의 사이드바 코드는 이제 여기에 위치하지 않습니다. 각 페이지에서 필요 시 구현)

    # --- 메인 화면: 프로젝트 목록 및 관리 ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("프로젝트 목록")
    with col2:
        if st.button("✚ 새 프로젝트 생성", type="primary", use_container_width=True):
            st.session_state.show_create_dialog = True
    
    # ... (이하 프로젝트 생성/수정/삭제 다이얼로그 및 테이블 표시 코드는 이전과 동일)
    # (이전 답변의 해당 부분을 여기에 복사-붙여넣기 하시면 됩니다.)
