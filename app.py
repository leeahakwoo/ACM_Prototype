# app.py (st.Page 파일 경로 수정 최종 버전)

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
# 파일 경로가 실제 pages/ 폴더 안의 파일 이름과 정확히 일치해야 합니다.
try:
    pg = st.navigation(
        [
            st.Page("app.py", title="대시보드", icon="🚀", default=True),
            st.Page("pages/1_거버넌스_관리.py", title="거버넌스 관리", icon="Ⓜ️"),
            st.Page("pages/2_문제정의.py", title="문제정의", icon="📋"),
            st.Page("pages/3_모델_설계.py", title="모델 설계", icon="🏗️"),
            st.Page("pages/4_모델_구현.py", title="모델 구현", icon="⚙️"),
            st.Page("pages/5_성능_검증.py", title="성능 검증", icon="📊"),
            st.Page("pages/6_거버넌스_검증.py", title="거버넌스 검증", icon="🛡️"),
        ]
    )
except Exception as e:
    st.error(f"페이지 네비게이션 설정 중 오류가 발생했습니다. 'pages' 폴더의 파일 이름을 확인해주세요.\n\n오류: {e}")
    st.stop()


# --- 페이지 기본 설정 ---
# st.set_page_config는 st.navigation 호출 전에 와야 한다는 암묵적인 규칙이 있을 수 있으므로 위로 이동.
# 또는 pg.run() 이후에 각 페이지에서 개별적으로 호출하는 것이 더 안정적일 수 있습니다.
# 여기서는 pg.run() 이후로 유지하되, 문제가 지속되면 각 페이지로 옮깁니다.


# --- 선택된 페이지 실행 ---
pg.run()


# --- 대시보드 페이지 콘텐츠 (app.py가 활성화될 때만 실행) ---
if pg.title == "대시보드":
    
    # st.set_page_config는 스크립트 최상단에서 한 번만 호출하는 것이 가장 안정적입니다.
    # 여기서는 이미 호출되었으므로, 타이틀만 다시 설정합니다.
    st.title("🚀 AI 관리 지원 도구")
    st.markdown("---")

    # --- session_state 관리 ---
    if 'editing_project_id' not in st.session_state:
        st.session_state.editing_project_id = None
    if 'selected_project_id' not in st.session_state:
        st.session_state.selected_project_id = None
    if 'show_create_dialog' not in st.session_state:
        st.session_state.show_create_dialog = False

    # --- 메인 화면: 프로젝트 목록 및 관리 ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("프로젝트 목록")
    with col2:
        if st.button("✚ 새 프로젝트 생성", type="primary", use_container_width=True):
            st.session_state.show_create_dialog = True
    
    # --- 다이얼로그 (팝업) 로직 ---
    if st.session_state.show_create_dialog:
        with st.dialog("새 프로젝트 생성"):
            with st.form("new_project_dialog_form"):
                name = st.text_input("프로젝트 이름")
                desc = st.text_area("프로젝트 설명")
                submitted = st.form_submit_button("생성하기")
                if submitted:
                    if name and create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.session_state.show_create_dialog = False
                        st.rerun()
                    # ... (이하 오류 처리)

    # --- 프로젝트 목록 테이블 ---
    projects = get_all_projects()
    # (이전 답변의 테이블 표시 및 관리 코드와 동일)
