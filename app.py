# app.py (최종 수정 버전)

import streamlit as st
from core.persistence import init_db, get_all_projects, create_project, delete_project, update_project
from datetime import datetime

# DB 초기화는 한 번만 실행
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- session_state 초기화 ---
if 'editing_project' not in st.session_state:
    st.session_state.editing_project = None

# --- 사이드바: 프로젝트 생성 또는 수정 ---
with st.sidebar:
    if st.session_state.editing_project:
        st.header("📝 프로젝트 수정")
        proj = st.session_state.editing_project
        with st.form("edit_project_form"):
            st.write(f"**ID: {proj['id']}**")
            name = st.text_input("프로젝트 이름", value=proj['name'])
            desc = st.text_area("프로젝트 설명", value=proj['description'])
            col1, col2 = st.columns(2)
            if col1.form_submit_button("저장하기", type="primary"):
                update_project(proj['id'], name, desc)
                st.toast("프로젝트가 수정되었습니다.")
                st.session_state.editing_project = None
                st.rerun()
            if col2.form_submit_button("취소"):
                st.session_state.editing_project = None
                st.rerun()
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기", type="primary"):
                if name:
                    if create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")

# --- 메인 화면: 프로젝트 목록 및 관리 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# 테이블 헤더
header_cols = st.columns([1, 3, 4, 2, 2])
header_cols[0].write("**ID**")
header_cols[1].write("**이름**")
header_cols[2].write("**설명**")
header_cols[3].write("**생성일**")
header_cols[4].write("**관리**")
st.divider()

if not projects:
    st.info("아직 생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 2])
        row_cols[0].write(proj['id'])
        row_cols[1].write(proj['name'])
        row_cols[2].write(proj['description'])
        dt_object = datetime.fromisoformat(proj['created_at'])
        row_cols[3].write(dt_object.strftime('%Y-%m-%d %H:%M'))
        
        button_col = row_cols[4]
        if button_col.button("수정", key=f"edit_{proj['id']}"):
            st.session_state.editing_project = proj
            st.rerun()
        
        button_col2 = row_cols[5]
        if button_col2.button("삭제", key=f"delete_{proj['id']}", type="secondary"):
            delete_project(proj['id'])
            st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
            st.rerun()
