# app.py (UI 개선 및 삭제 기능 추가)

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from core.persistence import init_db, get_all_projects, create_project, delete_project
from datetime import datetime

init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- 사이드바: 새 프로젝트 생성 ---
with st.sidebar:
    st.header("새 프로젝트 생성")
    with st.form("new_project_form"):
        new_proj_name = st.text_input("프로젝트 이름")
        new_proj_desc = st.text_area("프로젝트 설명")
        submitted = st.form_submit_button("생성하기")
        if submitted:
            if new_proj_name:
                create_project(new_proj_name, new_proj_desc)
                st.success(f"'{new_proj_name}' 프로젝트 생성 완료!")
                # 입력 필드 초기화를 위해 rerun
                st.rerun()
            else:
                st.error("프로젝트 이름을 입력해주세요.")

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# --- 핵심 수정 부분: 직접 테이블 UI 그리기 및 삭제 버튼 추가 ---
# 테이블 헤더
header_cols = st.columns([1, 3, 4, 2, 1])
header_cols[0].write("**ID**")
header_cols[1].write("**이름**")
header_cols[2].write("**설명**")
header_cols[3].write("**생성일**")
header_cols[4].write("**관리**")
st.divider()

if not projects:
    st.info("아직 생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # 각 프로젝트를 순회하며 행 생성
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 1])
        row_cols[0].write(proj['id'])
        row_cols[1].write(proj['name'])
        row_cols[2].write(proj['description'])
        # 날짜/시간 포맷 정리
        try:
            dt_object = datetime.fromisoformat(proj['created_at'])
            formatted_date = dt_object.strftime('%Y-%m-%d %H:%M')
            row_cols[3].write(formatted_date)
        except (ValueError, TypeError):
            row_cols[3].write(proj['created_at'])
        
        # 삭제 버튼
        if row_cols[4].button("삭제", key=f"delete_{proj['id']}", type="secondary"):
            delete_project(proj['id'])
            st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
            st.rerun()
