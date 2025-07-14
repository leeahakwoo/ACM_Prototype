# app.py (디자인 개선 최종 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")

# --- 커스텀 CSS 주입 ---
st.markdown("""
<style>
    /* 테이블 디자인 */
    .project-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden; /* 둥근 모서리를 위해 필수 */
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    .project-table th, .project-table td {
        padding: 16px 20px;
        text-align: left;
        border-bottom: 1px solid #E7EDF4;
        vertical-align: middle;
    }
    .project-table th {
        background-color: #F8FAFC;
        font-weight: 500;
        color: #49749C;
    }
    .project-table tr:last-child td {
        border-bottom: none;
    }
    .project-table tr:hover {
        background-color: #F1F5F9;
    }
    /* 버튼 스타일 조정 */
    .stButton>button {
        border-radius: 20px;
        padding: 6px 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- 헤더 구현 ---
# 디자인의 헤더를 st.columns로 유사하게 구현
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚀 MCP 기반 AI 개발 플랫폼")
with col2:
    # 검색, 알림, 프로필 아이콘 영역 (기능은 없지만 UI만 배치)
    sub_cols = st.columns([1, 1, 1, 3])
    sub_cols[0].button("🔍", help="검색 (구현 예정)", use_container_width=True)
    sub_cols[1].button("🔔", help="알림 (구현 예정)", use_container_width=True)
    sub_cols[2].button("👤", help="프로필 (구현 예정)", use_container_width=True)
st.divider()

# --- session_state 관리 ---
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None

# --- 사이드바: 프로젝트 생성/수정 ---
with st.sidebar:
    # 수정 모드
    if st.session_state.selected_project:
        st.header("📝 프로젝트 수정")
        proj = st.session_state.selected_project
        with st.form("edit_form"):
            name = st.text_input("프로젝트 이름", value=proj['name'])
            desc = st.text_area("프로젝트 설명", value=proj['description'])
            if st.form_submit_button("수정 완료", type="primary", use_container_width=True):
                update_project(proj['id'], name, desc)
                st.toast("프로젝트가 수정되었습니다.")
                st.session_state.selected_project = None # 선택 초기화
                st.rerun()
            if st.form_submit_button("취소", use_container_width=True):
                st.session_state.selected_project = None
                st.rerun()
    # 생성 모드
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기", use_container_width=True):
                if name and create_project(name, desc):
                    st.toast("프로젝트가 생성되었습니다.")
                    st.rerun()
                elif not name:
                    st.error("프로젝트 이름을 입력해주세요.")
                else:
                    st.error("프로젝트 생성에 실패했습니다.")

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

if not projects:
    st.info("생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # HTML 테이블 생성
    table_html = "<table class='project-table'><thead><tr><th>ID</th><th>이름</th><th>설명</th><th>생성일</th></tr></thead><tbody>"
    for proj in projects:
        dt_obj = datetime.fromisoformat(proj['created_at'])
        formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M')
        table_html += f"<tr><td>{proj['id']}</td><td>{proj['name']}</td><td>{proj['description']}</td><td>{formatted_date}</td></tr>"
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)
    
    # 수정 및 삭제를 위한 선택 UI
    st.markdown("---")
    st.subheader("프로젝트 관리")
    
    project_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in projects}
    selected_id_for_manage = st.selectbox("관리할 프로젝트를 선택하세요", options=project_options.keys(), format_func=lambda x: project_options[x])

    if selected_id_for_manage:
        col1, col2 = st.columns(2)
        
        # 수정 버튼
        if col1.button("선택한 프로젝트 수정", use_container_width=True):
            selected_proj_data = next((p for p in projects if p['id'] == selected_id_for_manage), None)
            st.session_state.selected_project = selected_proj_data
            st.rerun()
            
        # 삭제 버튼
        if col2.button("선택한 프로젝트 삭제", type="secondary", use_container_width=True):
            proj_name_to_delete = project_options[selected_id_for_manage]
            delete_project(selected_id_for_manage)
            st.toast(f"프로젝트 '{proj_name_to_delete}'가 삭제되었습니다.")
            st.rerun()
