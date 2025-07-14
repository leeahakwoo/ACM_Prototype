# app.py (메뉴 title 수정 최종 버전)

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
# 파일 경로는 실제 파일 이름(기존 이름)을 그대로 사용하고,
# title 파라미터만 원하는 메뉴명으로 변경합니다.
try:
    pg = st.navigation(
        [
            st.Page("app.py", title="대시보드", icon="🚀", default=True),
            st.Page("pages/0_MCP_관리.py", title="거버넌스 관리", icon="Ⓜ️"), 
            st.Page("pages/1_요구정의.py", title="문제정의", icon="📋"),
            st.Page("pages/2_설계.py", title="모델 설계", icon="🏗️"),
            st.Page("pages/3_구현.py", title="모델 구현", icon="⚙️"),
            st.Page("pages/4_성능_검증.py", title="성능 검증", icon="📊"),
            st.Page("pages/5_거버넌스_검토.py", title="거버넌스 검증", icon="🛡️"),
        ]
    )
except Exception as e:
    st.error(f"페이지 네비게이션 설정 중 오류가 발생했습니다. 'pages' 폴더의 파일 이름을 확인해주세요.\n\n오류: {e}")
    st.stop()

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 관리 지원 도구",
    page_icon="🚀",
    layout="wide",
)

# --- 선택된 페이지 실행 ---
pg.run()

# --- 대시보드 페이지 콘텐츠 ---
# 현재 페이지가 '대시보드'일 때만 아래 코드가 실행됩니다.
if pg.title == "대시보드":
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
    
    # 새 프로젝트 생성 다이얼로그
    if "show_create_dialog" in st.session_state and st.session_state.show_create_dialog:
        with st.dialog("새 프로젝트 생성"):
            with st.form("new_project_dialog_form"):
                name = st.text_input("프로젝트 이름")
                desc = st.text_area("프로젝트 설명")
                submitted = st.form_submit_button("생성하기")
                cancelled = st.form_submit_button("취소", type="secondary")
                if submitted:
                    if name and create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.session_state.show_create_dialog = False
                        st.rerun()
                    elif not name:
                        st.error("프로젝트 이름을 입력해주세요.")
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                if cancelled:
                    st.session_state.show_create_dialog = False
                    st.rerun()

    # 프로젝트 수정 다이얼로그
    if st.session_state.editing_project_id:
        proj_to_edit = next((p for p in get_all_projects() if p['id'] == st.session_state.editing_project_id), None)
        if proj_to_edit:
            with st.dialog("프로젝트 수정"):
                with st.form("edit_project_dialog_form"):
                    name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                    desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])
                    submitted_edit = st.form_submit_button("수정 완료")
                    submitted_cancel = st.form_submit_button("취소", type="secondary")
                    if submitted_edit:
                        update_project(proj_to_edit['id'], name, desc)
                        st.toast("프로젝트가 수정되었습니다.")
                        st.session_state.editing_project_id = None
                        st.rerun()
                    if submitted_cancel:
                        st.session_state.editing_project_id = None
                        st.rerun()

    # 프로젝트 목록 테이블
    projects = get_all_projects()
    header_cols = st.columns([1, 3, 4, 2, 2])
    header_cols[0].write("**ID**")
    header_cols[1].write("**이름**")
    header_cols[2].write("**설명**")
    header_cols[3].write("**생성일**")
    header_cols[4].write("**관리**")
    st.divider()

    if not projects:
        st.info("생성된 프로젝트가 없습니다.")
    else:
        for proj in projects:
            row_cols = st.columns([1, 3, 4, 2, 2])
            row_cols[0].write(proj['id'])
            row_cols[1].write(proj['name'])
            row_cols[2].write(proj['description'])
            try:
                dt_object = datetime.fromisoformat(proj['created_at'])
                row_cols[3].write(dt_object.strftime('%Y-%m-%d %H:%M'))
            except:
                row_cols[3].write(proj['created_at'])
            
            with row_cols[4]:
                manage_cols = st.columns(2)
                if manage_cols[0].button("수정", key=f"edit_{proj['id']}"):
                    st.session_state.editing_project_id = proj['id']
                    st.rerun()
                if manage_cols[1].button("삭제", key=f"delete_{proj['id']}", type="secondary"):
                    delete_project(proj['id'])
                    st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
                    st.rerun()
