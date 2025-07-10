# pages/3_구현.py (NameError 해결 버전)

import streamlit as st
from datetime import datetime
import sys
import os
import io
import re  # <--- 이 라인을 추가했습니다.

# --- 경로 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
from gemini_agent import generate_test_cases, convert_markdown_to_df, refine_content
import pandas as pd

st.set_page_config(page_title="구현 및 테스트", layout="wide")
st.title("⚙️ 구현 및 단위 테스트")
st.markdown("---")

# --- 1. 선택된 프로젝트 정보 확인 ---
selected_id = st.session_state.get('selected_project_id', None)
if not selected_id:
    st.error("선택된 프로젝트가 없습니다. 메인 페이지(app)로 돌아가 작업할 프로젝트를 먼저 선택해주세요.")
    st.stop()
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
    ("정상적인 입력값에 대한 기본 기능 검증", "일반적인 예외 상황 처리 검증", "부적절한 입력에 대한 방어 능력 검증")
)
if st.button("🤖 AI로 테스트 케이스 생성하기", type="primary", use_container_width=True):
    with st.spinner("Gemini 에이전트가 테스트 케이스를 작성하고 있습니다..."):
        generated_text = generate_test_cases(latest_design_doc, scenario)
        st.session_state['generated_test_cases_md'] = generated_text
        df = convert_markdown_to_df(generated_text)
        st.session_state['generated_test_cases_df'] = df
        st.rerun()

# --- 3. 생성 결과 확인, 발전 및 저장 ---
if 'generated_test_cases_df' in st.session_state and not st.session_state['generated_test_cases_df'].empty:
    st.subheader("Step 2: 생성된 테스트 케이스 발전시키기")
    
    edited_df = st.data_editor(
        st.session_state['generated_test_cases_df'],
        num_rows="dynamic",
        use_container_width=True,
        key="test_case_editor"
    )
    st.session_state['generated_test_cases_df'] = edited_df

    st.markdown("---")
    st.write("🤖 **AI 편집 도구모음**")
    
    current_md_table = edited_df.to_markdown(index=False)
    
    custom_instruction = st.text_input("직접 편집 지시하기 (예: TC-001과 유사한 테스트 케이스 2개 더 추가해줘)")
    if st.button("실행", disabled=not custom_instruction, key="custom_tc"):
        with st.spinner("AI가 당신의 지시를 수행하고 있습니다..."):
            instruction = f"""
            아래 마크다운 테이블 형식의 테스트 케이스 목록이 있습니다.
            이 목록에 대해 다음 지시사항을 수행하고, '수정된 전체 테스트 케이스 목록'을 동일한 마크다운 테이블 형식으로 반환해주세요.
            
            [지시사항]
            {custom_instruction}

            [원본 테스트 케이스 목록]
            {current_md_table}
            """
            refined_md = refine_content("", instruction)
            
            table_match = re.search(r'\|.*\|(?:\n\|.*\|)+', refined_md)
            if table_match:
                refined_md_table = table_match.group(0)
                st.session_state['generated_test_cases_md'] = refined_md_table
                st.session_state['generated_test_cases_df'] = convert_markdown_to_df(refined_md_table)
            else:
                st.warning("AI가 테이블 형식으로 응답하지 않았습니다. 원본 응답을 확인해주세요.")
                st.code(refined_md)

            st.rerun()
            
    st.markdown("---")
    st.subheader("Step 3: 최종본 저장 및 다운로드")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 이력으로 저장하기", use_container_width=True):
            final_md_to_save = st.session_state['generated_test_cases_df'].to_markdown(index=False)
            save_artifact(
                project_id=selected_id,
                stage="IMPLEMENT",
                type="TEST_CASE",
                content=final_md_to_save
            )
            st.success("테스트 케이스가 이력으로 저장되었습니다.")
            del st.session_state['generated_test_cases_md']
            del st.session_state['generated_test_cases_df']
            st.rerun()

    with col2:
        csv = st.session_state['generated_test_cases_df'].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📄 CSV 파일로 다운로드", csv, f"test_cases.csv", "text/csv", use_container_width=True)

# --- 4. 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 테스트 케이스 이력")
artifacts = get_artifacts_for_project(selected_id, "TEST_CASE")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 테스트 케이스가 없습니다.")
