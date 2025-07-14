# app.py (팝업 생성 기능 추가 버전)

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
if 'editing_project' not in st.session_state:
    st.session_state.editing_project = None
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None
if 'selected_project_name' not in st.session_state:
    st.session_state.selected_project_name = None
if 'show_create_dialog' not in st.session_state:
    st.session_state.show_create_dialog = False

# --- UI 그리기 ---
st.title("🚀 AI 관리 지원 도구")
st.header("대시보드")
st.markdown("---")

# --- 사이드바: 프로젝트 수정 전용 ---
# 이제 사이드바는 수정 모드일 때만 사용됩니다.
with st.sidebar:
    if st.session_state.editing_project:
        st.header("📝 프로젝트 수정")
        proj = st.session_state.editing_project
        with st.form("edit_form"):
            name = st.text_input("프로젝트 이름", value=proj['name'])
            desc = st.text_area("프로젝트 설명", value=proj['description'])
            if st.form_submit_button("수정 완료", type="primary"):
                update_project(proj['id'], name, desc)
                st.toast("프로젝트가 수정되었습니다.")
                st.session_state.editing_project = None
                st.rerun()
            if st.form_submit_button("취소"):
                st.session_state.editing_project = None
                st.rerun()
    else:
        st.info("프로젝트를 수정하려면 목록에서 '수정' 버튼을 클릭하세요.")


# --- 메인 콘텐츠: 프로젝트 목록 및 관리 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("프로젝트 목록")
with col2:
    # '새 프로젝트 생성' 버튼
    if st.button("✚ 새 프로젝트 생성", type="primary", use_container_width=True):
        st.session_state.show_create_dialog = True

# --- 새 프로젝트 생성 다이얼로그(팝업) ---
if st.session_state.show_create_dialog:
    with st.dialog("새 프로젝트 생성"):
        with st.form("new_project_dialog_form"):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            
            # Form 안에 두 개의 버튼을 두어 제출 로직을 분리
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.form_submit_button("생성하기"):
                if name:
                    if create_project(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.session_state.show_create_dialog = False
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")
            
            if col_btn2.form_submit_button("취소", type="secondary"):
                st.session_state.show_create_dialog = False
                st.rerun()

# --- 선택된 프로젝트 정보 표시 ---
# (이전 코드와 동일)
if st.session_state.selected_project_id:
    st.info(f"현재 작업 중인 프로젝트: **{st.session_state.selected_project_name}** (ID: {st.session_state.selected_project_id})")
else:
    st.info("작업할 프로젝트를 아래 목록에서 '선택' 버튼을 눌러 지정해주세요.")
st.divider()


# --- 프로젝트 목록 테이블 ---
projects = get_all_projects()
if not projects:
    st.info("생성된 프로젝트가 없습니다. '새 프로젝트 생성' 버튼을 클릭하여 시작하세요.")
else:
    # (테이블 표시 및 관리 버튼 코드는 이전과 동일)
    header_cols = st.columns([1, 3, 4, 2, 3])
    header_cols[0].write("**ID**")
    # ... (이하 동일)
    
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 3])
        # ... (이하 동일)
        with row_cols[4]:
            manage_cols = st.columns(3)
            if manage_cols[0].button("선택", ...):
                # ...
            if manage_cols[1].button("수정", ...):
                st.session_state.editing_project = proj # 수정은 이제 팝업이 아닌 사이드바에서 처리
                st.rerun()
            # ...
