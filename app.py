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
if 'selected_project_name' not in st.session_state:
    st.session_state.selected_project_name = None

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
                if name:
                    if create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")

# --- 메인 콘텐츠: 프로젝트 목록 ---
st.subheader("프로젝트 목록")
projects = get_all_projects()

if not projects:
    st.info("생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # 프로젝트 선택 UI
    project_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in projects}
    # 이전에 선택한 ID가 유효한지 확인하고, 아니면 첫 번째 프로젝트를 기본값으로 설정
    if st.session_state.selected_project_id not in project_options:
        st.session_state.selected_project_id = list(project_options.keys())[0] if project_options else None
    
    selected_id = st.radio(
        "작업할 프로젝트 선택:",
        options=list(project_options.keys()),
        format_func=lambda x: project_options.get(x),
        index=list(project_options.keys()).index(st.session_state.selected_project_id),
        horizontal=True,
        key="project_selector_radio"
    )
    # 선택 시 세션 상태 업데이트
    if selected_id:
        st.session_state.selected_project_id = selected_id
        st.session_state.selected_project_name = project_options.get(selected_id)
    
    st.divider()

    # 테이블 헤더
    header_cols = st.columns([1, 3, 4, 2, 2])
    header_cols[0].write("**ID**")
    header_cols[1].write("**이름**")
    header_cols[2].write("**설명**")
    header_cols[3].write("**생성일**")
    header_cols[4].write("**관리**")
    
    # 프로젝트 목록 표시
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 2])
        row_cols[0].write(proj['id'])
        row_cols[1].write(proj['name'])
        row_cols[2].write(proj['description'])
        try:
            dt_object = datetime.fromisoformat(proj['created_at'])
            row_cols[3].write(dt_object.strftime('%Y-%m-%d %H:%M'))
        except (ValueError, TypeError):
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
