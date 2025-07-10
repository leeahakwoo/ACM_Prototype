# app.py (디버깅 및 UX 개선 최종 버전)

import streamlit as st
from datetime import datetime
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 및 설정 ---
init_db()
st.set_page_config(page_title="MCP 기반 AI 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None

# --- 사이드바 ---
with st.sidebar:
    # 수정/생성 폼
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        proj_to_edit = next((p for p in get_all_projects() if p['id'] == st.session_state.editing_project_id), None)
        with st.form("edit_form"):
            name = st.text_input("프로젝트 이름", value=proj_to_edit['name'] if proj_to_edit else "")
            desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'] if proj_to_edit else "")
            if st.form_submit_button("수정 완료", type="primary"):
                update_project(st.session_state.editing_project_id, name, desc)
                st.session_state.editing_project_id = None
                st.rerun()
            if st.form_submit_button("취소"):
                st.session_state.editing_project_id = None
                st.rerun()
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기"):
                if name:
                    if create_project(name, desc) is not None:
                        st.toast("프로젝트가 생성되었습니다.")
                    else:
                        st.error("프로젝트 생성에 실패했습니다. (이름 중복 가능성)")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")

    # 디버깅 정보 표시
    with st.expander("🛠️ 디버깅 정보"):
        st.write(f"Editing ID: {st.session_state.editing_project_id}")
        projects_count = len(get_all_projects())
        st.write(f"DB 프로젝트 수: {projects_count}")

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# (이하 프로젝트 목록 표시는 이전과 동일)
...
