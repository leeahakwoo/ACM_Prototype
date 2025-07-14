# app.py (Back to Basics 최종 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import (가장 먼저) ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 페이지 기본 설정 (앱 전체에서 단 한 번만 호출) ---
st.set_page_config(
    page_title="AI 관리 지원 도구",
    page_icon="🚀",
    layout="wide",
)

# --- 앱 초기화 ---
init_db()

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None

# --- UI 그리기 ---
st.title("🚀 AI 관리 지원 도구")
st.header("대시보드")
st.markdown("---")

# --- 사이드바 ---
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
                elif not name: st.error("프로젝트 이름을 입력해주세요.")
                else: st.error("이미 존재하는 프로젝트 이름입니다.")

# --- 메인 콘텐츠: 프로젝트 목록 ---
st.subheader("프로젝트 목록")
projects = get_all_projects()

if not projects:
    st.info("생성된 프로젝트가 없습니다.")
else:
    # 프로젝트 선택 UI
    project_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in projects}
    if st.session_state.selected_project_id not in project_options:
        st.session_state.selected_project_id = list(project_options.keys())[0] if project_options else None
    
    st.session_state.selected_project_id = st.radio(
        "작업할 프로젝트 선택:",
        options=list(project_options.keys()),
        format_func=lambda x: project_options.get(x),
        horizontal=True,
        key="project_selector_radio"
    )
    st.session_state.selected_project_name = project_options.get(st.session_state.selected_project_id)
    st.divider()

    # 테이블 헤더
    header_cols = st.columns([1, 3, 4, 2, 2])
    # ... (이하 테이블 표시 및 관리 버튼 코드는 이전과 동일)
