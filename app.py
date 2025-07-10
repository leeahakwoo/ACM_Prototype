# app.py (고도화 버전)
import streamlit as st
from core.persistence import init_db, get_all_projects, create_project
import pandas as pd

# DB 초기화 (앱 실행 시 한 번만)
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

st.sidebar.header("새 프로젝트 생성")
new_proj_name = st.sidebar.text_input("프로젝트 이름")
new_proj_desc = st.sidebar.text_area("프로젝트 설명")
if st.sidebar.button("생성하기", type="primary"):
    if new_proj_name:
        create_project(new_proj_name, new_proj_desc)
        st.sidebar.success(f"'{new_proj_name}' 프로젝트 생성 완료!")
        st.rerun()
    else:
        st.sidebar.error("프로젝트 이름을 입력해주세요.")

st.header("프로젝트 목록")
projects = get_all_projects()
if projects:
    df = pd.DataFrame(projects, columns=["ID", "이름", "설명", "생성일"])
    st.dataframe(df, use_container_width=True)
    st.info("작업할 프로젝트를 선택하고 왼쪽 사이드바에서 개발 단계로 이동하세요. (향후 프로젝트 선택 기능 추가 예정)")
else:
    st.info("아직 생성된 프로젝트가 없습니다. 왼쪽 사이드바에서 새 프로젝트를 생성해주세요.")
