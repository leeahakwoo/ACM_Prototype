# pages/3_구현.py

import streamlit as st
from datetime import datetime
import sys
import os
import io

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_test_cases, convert_markdown_to_df
import pandas as pd

st.set_page_config(page_title="구현 및 테스트", layout="wide")
st.title("⚙️ 구현 및 단위 테스트")
st.markdown("---")

# --- 1. 선택된 프로젝트 정보 확인 ---
selected_id = st.session_state.get('selected_project_id', None)

if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()

# 해당 프로젝트의 최신 '모델 설계서' 불러오기
design_doc_artifacts = get_artifacts_for_project(selected_id, "MODEL_DESIGN")

if not design_doc_artifacts:
    st.warning("이 프로젝트에 대한 '모델 설계서'가 없습니다. '설계' 페이지에서 먼저 작성해주세요.")
    st.stop()

latest_design_doc = design_doc_artifacts[0]['content']

st.header(f"프로젝트: {st.session_state.get('selected_project_name', 'N/A')}")
with st.expander("참고: 이 프로젝트의 모델 설계서 보기"):
    st.markdown(latest_design_doc)

# --- 2. 단위 테스트 케이스 생성기 ---
st.subheader("Step 1: 단위 테스트 케이스(Unit Test Case) 생성")

scenario = st.selectbox(
    "어떤 시나리오에 대한 테스트 케이스를 생성할까요?",
    (
        "정상적인 입력값에 대한 기본 기능 검증",
        "일반적인 예외 상황 처리 검증 (예: 빈 값, 특수문자)",
        "공격적이거나 부적절한 입력에 대한 방어 능력 검증",
        "경계값 분석(Boundary-value analysis)을 위한 테스트 케이스",
        "사용자가 직접 시나리오 입력"
    )
)

if scenario == "사용자가 직접 시나리오 입력":
    scenario_custom = st.text_input("테스트하고 싶은 시나리오를 직접 입력하세요:")
    final_scenario = scenario_custom
else:
    final_scenario = scenario

if st.button("🤖 AI로 테스트 케이스 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 모델 설계서 기반으로 테스트 케이스를 작성하고 있습니다..."):
        generated_text = generate_test_cases(latest_design_doc, final_scenario)
        st.session_state['generated_test_cases_md'] = generated_text
        
        # 마크다운을 DataFrame으로 변환하여 state에 저장
        df = convert_markdown_to_df(generated_text)
        st.session_state['generated_test_cases_df'] = df

# --- 3. 생성 결과 확인 및 저장/다운로드 ---
if 'generated_test_cases_md' in st.session_state and not st.session_state['generated_test_cases_df'].empty:
    st.subheader("📝 생성된 단위 테스트 케이스")
    
    df_result = st.session_state['generated_test_cases_df']
    st.dataframe(df_result, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    
    # DB 저장 버튼
    with col1:
        if st.button("💾 이력으로 저장하기", use_container_width=True):
            # 마크다운 원본 텍스트를 저장
            save_artifact(
                project_id=selected_id,
                stage="IMPLEMENT",
                type="TEST_CASE",
                content=st.session_state['generated_test_cases_md']
            )
            st.success("테스트 케이스가 이력으로 저장되었습니다.")

    # CSV 다운로드 버튼
    with col2:
        csv = df_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 CSV 파일로 다운로드",
            data=csv,
            file_name=f"test_cases_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # DOCX 다운로드 (향후 추가 가능)
    with col3:
        st.button("📄 DOCX 파일로 다운로드 (준비 중)", disabled=True, use_container_width=True)


# --- 4. 저장된 이력 ---
st.markdown("---")
st.subheader("📜 저장된 테스트 케이스 이력")
artifacts = get_artifacts_for_project(selected_id, "TEST_CASE")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 테스트 케이스가 없습니다.")
