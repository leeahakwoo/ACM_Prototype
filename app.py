# your_mcp_project/app.py

import streamlit as st

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(
    page_title="AI 개발 문서 자동화 MCP",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- session_state 초기화 --------------------
# 앱이 처음 실행되거나 새로고침될 때 session_state를 초기화합니다.
# 각 페이지에서 입력받을 데이터들을 미리 딕셔너리 형태로 선언해둡니다.

# 문제 정의서 데이터
if 'problem_definition' not in st.session_state:
    st.session_state['problem_definition'] = {
        "project_name": "",
        "project_goal": "",
        "problem_background": "",
        "expected_output": ""
    }

# 모델 정의서 데이터
if 'model_spec' not in st.session_state:
    st.session_state['model_spec'] = {
        "model_name": "",
        "model_type": "분류",
        "key_features": "",
        "hyperparameters": ""
    }

# 모델 검증 데이터 (이 페이지에서는 생성되지만, 일단 틀만 잡아둡니다)
if 'model_validation' not in st.session_state:
    st.session_state['model_validation'] = {
        "validation_metrics": {},
        "summary": ""
    }

# -------------------- 메인 페이지 콘텐츠 --------------------

st.title("📄 AI 개발 문서 자동화 MCP")

st.markdown("---")

st.header("🚀 프로젝트 소개")
st.markdown("""
이 애플리케이션은 AI 모델 개발 과정에서 필요한 주요 문서들을 자동화하고 관리하기 위한 **최소 기능 제품(Minimum Viable Product, MCP)**입니다.
각 단계별로 필요한 정보들을 입력하면, 최종적으로 정리된 문서를 확인하고 공유할 수 있습니다.

**주요 기능:**
- **문제 정의서 작성**: 프로젝트의 목표와 배경을 정의합니다.
- **모델 정의서 작성**: 사용할 AI 모델의 상세 사양을 기록합니다.
- **모델 검증 결과 확인**: 모델의 성능 지표를 시각화하고 분석합니다.
""")

st.info("👈 왼쪽 사이드바에서 작업할 페이지를 선택하세요.", icon="ℹ️")

st.markdown("---")
st.write("Made with ❤️ by a Senior Streamlit Developer")
