# app.py (st.navigation 제거, 안정 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="대시보드 - AI 관리 지원 도구", # 브라우저 탭에 표시될 이름
    page_icon="🚀",
    layout="wide",
)

# --- 타이틀 ---
st.title("🚀 AI 관리 지원 도구")
st.markdown("---")

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None

# --- 사이드바: 프로젝트 생성/수정 ---
# (이 부분은 이전 답변의 코드를 그대로 사용해도 좋습니다. 
#  단, dialog 대신 사이드바에 다시 배치하는 것이 더 안정적일 수 있습니다.)
with st.sidebar:
    # 수정 모드
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        proj_to_edit = next((p for p in get_all_projects() if p['id'] == st.session_state.editing_project_id), None)
        if proj_to_edit:
            with st.form("edit_form"):
                name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])
                if st.form_submit_button("수정 완료", type="primary"):
                    update_project(st.session_state.editing_project_id, name, desc)
                    st.toast("프로젝트가 수정되었습니다.")
                    st.session_state.editing_project_id = None
                    st.rerun()
                if st.form_submit_button("취소"):
                    st.session_state.editing_project_id = None
                    st.rerun()
    # 생성 모드
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기"):
                if name and create_project(name, desc):
                    st.toast("프로젝트가 생성되었습니다.")
                    st.rerun()
                # ... (오류 처리)

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# (이전 답변의 테이블 표시 및 관리 버튼 코드와 동일)
# ...
