# app.py

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 (가장 먼저 실행) ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None

# --- 함수 정의 ---
def switch_to_edit_mode(project_id):
    st.session_state.editing_project_id = project_id
    st.rerun()

def switch_to_create_mode():
    st.session_state.editing_project_id = None
    st.rerun()

# --- 사이드바 UI ---
with st.sidebar:
    # (생성/수정 폼 코드는 이전과 동일)
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        proj_to_edit = next((p for p in get_all_projects() if p['id'] == st.session_state.editing_project_id), None)
        if proj_to_edit:
            with st.form("edit_form"):
                name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("저장", type="primary"):
                    update_project(st.session_state.editing_project_id, name, desc)
                    st.toast("프로젝트가 수정되었습니다.")
                    switch_to_create_mode()
                if col2.form_submit_button("취소"):
                    switch_to_create_mode()
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기"):
                if name:
                    if create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

if not projects:
    st.info("생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # --- 핵심 추가: 프로젝트 선택 UI ---
    project_names = [p['name'] for p in projects]
    # session_state에 저장된 프로젝트가 있다면 그 이름으로 기본값 설정
    if st.session_state.selected_project_id:
        try:
            default_name = next(p['name'] for p in projects if p['id'] == st.session_state.selected_project_id)
            default_index = project_names.index(default_name)
        except (StopIteration, ValueError):
            default_index = 0
    else:
        default_index = 0

    selected_name = st.radio(
        "작업할 프로젝트 선택:",
        project_names,
        index=default_index,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # 선택된 프로젝트의 ID를 session_state에 저장
    selected_project = next((p for p in projects if p['name'] == selected_name), None)
    if selected_project:
        st.session_state.selected_project_id = selected_project['id']

    st.divider()

    # 테이블 헤더
    header_cols = st.columns([1, 3, 4, 2, 2])
    # ... (이하 테이블 표시 및 관리 버튼 코드는 이전과 동일) ...
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 2])
        # ... (이전 코드와 동일)
