# app.py (최종 디버깅 완료 버전)

import streamlit as st
import sys
import os
from datetime import datetime

# --- 경로 설정 (가장 먼저 실행) ---
# 이 코드는 항상 파일의 맨 위에 있어야 합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 경로 설정 후 다른 모듈 import
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
# DB 초기화는 한 번만 실행
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")
st.markdown("---")

# --- session_state 관리 ---
# 수정 모드를 위한 상태 초기화
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None

# --- 사이드바 UI ---
with st.sidebar:
    # 수정 모드일 때와 생성 모드일 때를 분리
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        
        # 현재 수정 중인 프로젝트 정보 찾기
        all_projects = get_all_projects()
        proj_to_edit = next((p for p in all_projects if p['id'] == st.session_state.editing_project_id), None)

        if proj_to_edit:
            new_name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
            new_desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])

            col1, col2 = st.columns(2)
            if col1.button("저장", type="primary"):
                update_project(st.session_state.editing_project_id, new_name, new_desc)
                st.toast("프로젝트가 수정되었습니다.")
                st.session_state.editing_project_id = None
                st.rerun()
            if col2.button("취소"):
                st.session_state.editing_project_id = None
                st.rerun()
    else:
        st.header("새 프로젝트 생성")
        name_input = st.text_input("프로젝트 이름")
        desc_input = st.text_area("프로젝트 설명")
        if st.button("생성하기", type="primary"):
            if name_input:
                if create_project(name_input, desc_input):
                    st.toast(f"'{name_input}' 프로젝트 생성 완료!")
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
