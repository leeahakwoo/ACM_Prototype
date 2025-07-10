# app.py (AttributeError 해결 및 로직 최종 단순화)

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
# st.session_state를 사용하여 현재 수정 중인 프로젝트 ID를 관리합니다.
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None

# --- 함수 정의 ---
def switch_to_edit_mode(project_id):
    """수정 모드로 전환하는 함수"""
    st.session_state.editing_project_id = project_id

def switch_to_create_mode():
    """생성 모드로 전환하는 함수"""
    st.session_state.editing_project_id = None

# --- 사이드바 UI ---
with st.sidebar:
    # 수정 모드일 때
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        
        # 현재 수정 중인 프로젝트 정보 찾기
        proj_to_edit = next((p for p in get_all_projects() if p['id'] == st.session_state.editing_project_id), None)
        
        if proj_to_edit:
            with st.form("edit_form"):
                name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])
                
                # 버튼을 가로로 배치
                col1, col2 = st.columns(2)
                if col1.form_submit_button("저장", type="primary"):
                    update_project(st.session_state.editing_project_id, name, desc)
                    st.toast("프로젝트가 수정되었습니다.")
                    switch_to_create_mode() # 생성 모드로 전환
                    st.rerun() # ★★★ st.experimental_rerun() -> st.rerun() 으로 변경
                if col2.form_submit_button("취소"):
                    switch_to_create_mode() # 생성 모드로 전환
                    st.rerun() # ★★★ st.experimental_rerun() -> st.rerun() 으로 변경

    # 생성 모드일 때
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            
            if st.form_submit_button("생성하기"):
                if name:
                    if create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.rerun() # ★★★ st.experimental_rerun() -> st.rerun() 으로 변경
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
    st.info("생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
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
        
        # 수정 버튼
        if row_cols[4].button("수정", key=f"edit_{proj['id']}"):
            switch_to_edit_mode(proj['id'])
            st.rerun() # ★★★ st.experimental_rerun() -> st.rerun() 으로 변경
        
        # 삭제 버튼
        if row_cols[5].button("삭제", key=f"delete_{proj['id']}", type="secondary"):
            delete_project(proj['id'])
            st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
            st.rerun() # ★★★ st.experimental_rerun() -> st.rerun() 으로 변경
