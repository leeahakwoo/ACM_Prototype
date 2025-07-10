# app.py (프로젝트 관리 기능 최종 버전)

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from core.persistence st.session_state.editing_project:
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
                st.session_state.editing_project = None # 수정 모드 종료
                st.rerun()
            if col2.form_submit_button("취소"):
                st.session_state.editing_project = None # 수정 모 import init_db, get_all_projects, create_project, update_project, delete_project
from datetime import datetime

init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")
st.markdown("---")

# --- session_state 초기화 ---
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None
if 'editing_project' not in st.session_state:
    st.session_state.editing_project = None

# --- 메인 화면: 프로젝트 목록 및 선택 ---
st.header("프로젝트 목록")
projects = get_all_projects()

if not projects:
    st.info("아직 생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # st.radio를 사용하여 프로젝트 선택
    project_names = [p['name'] for p in projects]
    
    # 이전에 선택한 프로젝트가 있다면 그 인덱스를 유지
    try:
        selected_index = project_names.index(st.session_state.get('selected_project드 종료
                st.rerun()

    # 생성 모드일 때 (기본)
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기", type="primary"):
                if name:
                    create_project(name, desc)
                    st.toast("프로젝트가 생성되었습니다.")
                    st.rerun()
                else:
                    st.error("프로젝트 이름을 입력해주세요.")

# --- 메인 화면: 프로젝트 목록 및 관리 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# 체크박스를 위한 딕셔너리 초기화
if 'selected_projects' not in st.session_state:
    st.session_state.selected_projects = {proj['id']: False for proj in projects}

# 테이블 헤더
header_cols = st.columns([0.5, 1, 3, 4, 2, 2])
header_cols[0_name', ''))
    except ValueError:
        selected_index = 0

    selected_name = st.radio(
        "작업할 프로젝트를 선택하세요:",
        project_names,
        index=selected_index,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # 선택된 프로젝트 정보 업데이트
    selected_project = next((p for p in projects if p['name'] == selected_name), None)
    if selected_project:
        st.session_state.selected_project_id = selected_project['id']
        st.session_state.selected_project_name = selected_project['name']

        # 선택된 프로젝트 정보 및 관리 버튼 표시
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                st.subheader(f"선택된 프로젝트: {selected_project['name']}")
                st.caption(f"ID: {selected_project['id']}")
            with col2:
                st.write("**설명:**")
                st.write(selected_project['description'] or "설명 없음")
            ].write("") # 체크박스용
header_cols[1].write("**ID**")
header_cols[2].write("**이름**")
header_cols[3].write("**설명**")
header_cols[4].write("**생성일**")
header_cols[5].write("**관리**")
st.divider()

if not projects:
    st.info("생성된 프로젝트가 없습니다.")
else:
    for proj in projects:
        row_cols = st.columns([0.5, 1, 3, 4, 2, 2])
        
        # 체크박스
        st.session_state.selected_projects[proj['id']] = row_cols[0].checkbox("", key=f"select_{proj['id']}")
        
        # 데이터 표시
        row_cols[1].write(proj['id'])
        row_cols[2].write(proj['name'])
        row_cols[3].write(proj['description'])
        
        dt_object = datetime.fromisoformat(proj['created_at'])
        row_cols[4].write(dt_object.strftime('%Y-%m-%d %H:%M'))
        
        # 관리 버튼 (수정, 삭제)
        if row_cols[5].button("with col3:
                # 수정 버튼
                if st.button("수정", key=f"edit_{selected_project['id']}"):
                    st.session_state.editing_project = selected_project
                    st.rerun() # 사이드바를 업데이트하기 위해 새로고침
                # 삭제 버튼
                if st.button("삭제", key=f"delete_{selected_project['id']}", type="secondary"):
                    delete_project(selected_project['id'])
                    st.toast(f"프로젝트 '{selected_project['name']}'가 삭제되었습니다.")
                    # 삭제 후 선택 초기화
                    st.session_state.selected_project_id = None
                    st.session_state.selected_project_name = None
                    st.rerun()

# --- 사이드바: 프로젝트 생성 또는 수정 ---
with st.sidebar:
    # 수정 모드일 때
    if st.session_state.editing_project:
        st.header("프로젝트 수정")
        editing_proj = st.session_state.editing_project
        with st.form("edit_project_form"):
            name = st.text_input("프로젝트 이름", value=editing_proj['name'])
            desc = st.text_area("프로젝트 설명", value=editing_proj['description'])
            
            submitted = st.form_submit_button("수정 완료")
            if submitted:
                update_project(editing_proj['id'], name,수정", key=f"edit_{proj['id']}"):
            st.session_state.editing_project = proj # 수정 모드로 전환
            st.rerun()

# 선택 항목 일괄 삭제 버튼
st.markdown("---")
selected_ids = [pid for pid, selected in st.session_state.selected_projects.items() if selected]

if selected_ids:
    if st.button(f"{len(selected_ids)}개 프로젝트 삭제", type="secondary"):
        for pid in selected_ids:
            delete_project(pid)
        st.toast(f"{len(selected_ids)}개의 프로젝트가 삭제되었습니다.")
        # 체크박스 상태 초기화
        st.session_state.selected_projects = {proj['id']: False desc)
                st.success("프로젝트가 수정되었습니다.")
                st.session_state.editing_project = None # 수정 모드 종료
                st.rerun()
        if st.button("수정 취소"):
            st.session_state.editing_project = None
            st.rerun()
    # 생성 모드일 때
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form"):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            
            submitted = st.form_submit_button("생성하기")
            if submitted:
                if name:
                    if create_project(name, desc):
                        st.success(f"'{name}' 프로젝트 생성 완료!")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error("프로젝트 이름을 입력해주세요.")
