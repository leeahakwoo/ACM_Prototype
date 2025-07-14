# app.py (인터랙티브 테이블 UI 최종 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="대시보드 - AI 관리 지원 도구", page_icon="🚀", layout="wide")

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
                if name and create_project(name, desc):
                    st.toast("프로젝트가 생성되었습니다.")
                    st.rerun()
                elif not name: st.error("프로젝트 이름을 입력해주세요.")
                else: st.error("이미 존재하는 프로젝트 이름입니다.")

# --- 메인 콘텐츠: 프로젝트 목록 ---
st.subheader("프로젝트 목록")
projects = get_all_projects()

# 현재 선택된 프로젝트 정보 표시
if st.session_state.selected_project_id:
    st.info(f"현재 작업 중인 프로젝트: **{st.session_state.selected_project_name}** (ID: {st.session_state.selected_project_id})")
else:
    st.info("작업할 프로젝트를 아래 목록에서 '선택' 버튼을 눌러 지정해주세요.")
st.divider()

if not projects:
    st.info("생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # 테이블 헤더
    header_cols = st.columns([1, 3, 4, 2, 3])
    header_cols[0].write("**ID**")
    header_cols[1].write("**이름**")
    header_cols[2].write("**설명**")
    header_cols[3].write("**생성일**")
    header_cols[4].write("**관리**")
    
    # 프로젝트 목록 표시
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 3])
        row_cols[0].write(proj['id'])
        row_cols[1].write(proj['name'])
        row_cols[2].write(proj['description'])
        try:
            dt_object = datetime.fromisoformat(proj['created_at'])
            row_cols[3].write(dt_object.strftime('%Y-%m-%d %H:%M'))
        except (ValueError, TypeError):
            row_cols[3].write(proj['created_at'])
        
        # 관리 버튼 컬럼
        with row_cols[4]:
            manage_cols = st.columns([1, 1, 1])
            
            # 선택 버튼
            is_selected = (st.session_state.selected_project_id == proj['id'])
            if manage_cols[0].button(
                "✓ 선택" if is_selected else "선택", 
                key=f"select_{proj['id']}", 
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_project_id = proj['id']
                st.session_state.selected_project_name = proj['name']
                st.rerun()

            # 수정 버튼
            if manage_cols[1].button("수정", key=f"edit_{proj['id']}"):
                st.session_state.editing_project_id = proj['id']
                st.rerun()
            
            # 삭제 버튼
            if manage_cols[2].button("삭제", key=f"delete_{proj['id']}"):
                delete_project(proj['id'])
                st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
                if st.session_state.selected_project_id == proj['id']:
                    st.session_state.selected_project_id = None
                    st.session_state.selected_project_name = None
                st.rerun()
