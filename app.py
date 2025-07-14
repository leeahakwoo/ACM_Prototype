# app.py (파일 경로 최종 수정 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

# --- 페이지 정의 (st.Page 사용) ---
# *** 여기의 파일 경로가 실제 pages/ 폴더 안의 파일 이름과 정확히 일치해야 합니다. ***
try:
    pg = st.navigation(
        [
            st.Page("app.py", title="대시보드", icon="🚀", default=True),
            # '거버넌스 관리'에 해당하는 파일이 '0_MCP_관리.py'라고 가정하고 경로를 수정합니다.
            st.Page("pages/0_MCP_관리.py", title="거버넌스 관리", icon="Ⓜ️"), 
            st.Page("pages/2_문제정의.py", title="문제정의", icon="📋"),
            st.Page("pages/3_모델_설계.py", title="모델 설계", icon="🏗️"),
            st.Page("pages/4_모델_구현.py", title="모델 구현", icon="⚙️"),
            st.Page("pages/5_성능_검증.py", title="성능 검증", icon="📊"),
            st.Page("pages/6_거버넌스_검증.py", title="거버넌스 검증", icon="🛡️"),
        ]
    )
except Exception as e:
    st.error(f"페이지 네비게이션 설정 중 오류가 발생했습니다. 'pages' 폴더의 파일 이름을 확인해주세요.\n\n오류: {e}")
    st.stop()

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 관리 지원 도구",
    page_icon="🚀",
    layout="wide",
)

# --- 선택된 페이지 실행 ---
pg.run()

# --- 대시보드 페이지 콘텐츠 ---
# 현재 페이지가 '대시보드'일 때만 아래 코드가 실행됩니다.
if pg.title == "대시보드":
    st.title("🚀 AI 관리 지원 도구")
    st.markdown("---")

    # (이하 프로젝트 생성/수정/삭제 및 목록 표시 코드는 이전 답변과 동일합니다)
    # (코드가 길어 생략. 이전 답변의 해당 부분을 그대로 사용하시면 됩니다)
    # ...
