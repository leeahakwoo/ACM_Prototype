# app.py (UI/UX 최종 개선 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

# --- 페이지 기본 설정 (서비스 명칭 변경) ---
st.set_page_config(
    page_title="대시보드 - AI 관리 지원 도구",
    page_icon="🚀",
    layout="wide",
    menu_items={
        'About': "MCP 기반 AI 개발 및 거버넌스 지원 도구입니다."
    }
)

# --- 커스텀 CSS ---
# (이전과 동일)
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 

# --- 타이틀 (서비스 명칭 변경) ---
st.title("🚀 AI 관리 지원 도구")
st.markdown("---")


# --- 메인 화면: 프로젝트 목록 및 관리 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.header("프로젝트 목록")
with col2:
    # '새 프로젝트 생성' 버튼을 메인 화면 오른쪽 상단에 배치
    if st.button("✚ 새 프로젝트 생성", type="primary", use_container_width=True):
        st.session_state.show_create_dialog = True

# 새 프로젝트 생성을 위한 다이얼로그(팝업)
# st.dialog는 실험적 기능(experimental)입니다.
if "show_create_dialog" in st.session_state and st.session_state.show_create_dialog:
    with st.dialog("새 프로젝트 생성"):
        with st.form("new_project_dialog_form"):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            
            # Form 안에 두 개의 버튼을 두어 제출 로직을 분리
            submitted = st.form_submit_button("생성하기")
            cancelled = st.form_submit_button("취소", type="secondary")

            if submitted:
                if name:
                    if create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.session_state.show_create_dialog = False
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")
            if cancelled:
                st.session_state.show_create_dialog = False
                st.rerun()


# --- 프로젝트 목록 테이블 ---
# (이전과 동일한 테이블 UI 및 관리 기능)
projects = get_all_projects()
# ... (이전 답변의 테이블 표시 및 관리 코드와 동일)

# --- 프로젝트 수정/삭제를 위한 세션 상태 관리 ---
if 'editing_project' not in st.session_state:
    st.session_state.editing_project = None

# 수정 모드 다이얼로그
if st.session_state.editing_project:
    proj = st.session_state.editing_project
    with st.dialog("프로젝트 수정"):
        with st.form("edit_project_dialog_form"):
            name = st.text_input("프로젝트 이름", value=proj['name'])
            desc = st.text_area("프로젝트 설명", value=proj['description'])
            
            submitted_edit = st.form_submit_button("수정 완료")
            submitted_cancel = st.form_submit_button("취소", type="secondary")
            
            if submitted_edit:
                update_project(proj['id'], name, desc)
                st.toast("프로젝트가 수정되었습니다.")
                st.session_state.editing_project = None
                st.rerun()
            if submitted_cancel:
                st.session_state.editing_project = None
                st.rerun()

# 테이블 헤더
# ... (이하 코드는 이전과 동일)
