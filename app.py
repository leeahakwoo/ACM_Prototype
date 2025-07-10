# app.py (데이터 표시 오류 최종 수정 버전)

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from core.persistence import init_db, get_all_projects, create_project, delete_project
from datetime import datetime

# DB 초기화는 한 번만 실행
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- 사이드바: 새 프로젝트 생성 ---
with st.sidebar:
    st.header("새 프로젝트 생성")
    # st.form을 사용하면 버튼을 눌렀을 때만 전체 입력값이 한 번에 처리됩니다.
    with st.form("new_project_form", clear_on_submit=True):
        new_proj_name = st.text_input("프로젝트 이름")
        new_proj_desc = st.text_area("프로젝트 설명")
        submitted = st.form_submit_button("생성하기")
        if submitted:
            if new_proj_name:
                create_project(new_proj_name, new_proj_desc)
                st.success(f"'{new_proj_name}' 프로젝트 생성 완료!")
                # 페이지를 새로고침하여 목록에 즉시 반영
                st.rerun()
            else:
                st.error("프로젝트 이름을 입력해주세요.")

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# --- 핵심 수정 부분: Pandas를 사용하지 않고 직접 데이터 표시 ---
# 테이블 헤더
header_cols = st.columns([1, 3, 4, 2, 1])
with header_cols[0]:
    st.write("**ID**")
with header_cols[1]:
    st.write("**이름**")
with header_cols[2]:
    st.write("**설명**")
with header_cols[3]:
    st.write("**생성일**")
with header_cols[4]:
    st.write("**관리**")
st.divider()

if not projects:
    st.info("아직 생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
else:
    # 각 프로젝트(딕셔너리)를 순회하며 행 생성
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 1])
        
        # 딕셔너리 키로 값에 직접 접근
        with row_cols[0]:
            st.write(proj['id'])
        with row_cols[1]:
            st.write(proj['name'])
        with row_cols[2]:
            st.write(proj['description'])
        with row_cols[3]:
            # 날짜/시간 포맷 정리
            try:
                dt_object = datetime.fromisoformat(proj['created_at'])
                formatted_date = dt_object.strftime('%Y-%m-%d %H:%M')
                st.write(formatted_date)
            except (ValueError, TypeError):
                st.write(proj['created_at'])
        
        # 삭제 버튼
        with row_cols[4]:
            if st.button("삭제", key=f"delete_{proj['id']}", type="secondary"):
                delete_project(proj['id'])
                st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
                st.rerun()
