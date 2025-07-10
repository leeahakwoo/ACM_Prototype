# app.py

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 (가장 먼저 실행) ---
# 이 코드는 항상 파일의 맨 위에 있어야 합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None

# --- 사이드바 ---
with st.sidebar:
    # 수정 모드일 때
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        all_projects_for_edit = get_all_projects()
        proj_to_edit = next((p for p in all_projects_for_edit if p['id'] == st.session_state.editing_project_id), None)
        
        if proj_to_edit:
            with st.form("edit_form"):
                name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])
                
                # 수정/취소 버튼
                submitted_edit = st.form_submit_button("수정 완료", type="primary")
                submitted_cancel = st.form_submit_button("취소")

                if submitted_edit:
                    update_project(st.session_state.editing_project_id, name, desc)
                    st.toast("프로젝트가 수정되었습니다.")
                    st.session_state.editing_project_id = None
                    st.rerun()
                if submitted_cancel:
                    st.session_state.editing_project_id = None
                    st.rerun()

    # 생성 모드일 때
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            submitted_create = st.form_submit_button("생성하기")
            
            if submitted_create:
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

# 테이블 헤더
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
        except (ValueError, TypeError):
            row_cols[3].write(proj['created_at'])
        
        # 수정 버튼
        if row_cols[4].button("수정", key=f"edit_{proj['id']}"):
            st.session_state.editing_project_id = proj['id']
            st.rerun()
        
        # 삭제 버튼
        if row_cols[5].button("삭제", key=f"delete_{proj['id']}", type="secondary"):
            delete_project(proj['id'])
            st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
            st.rerun()
