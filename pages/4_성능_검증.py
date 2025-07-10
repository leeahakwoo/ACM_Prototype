# pages/4_성능_검증.py (콘텐츠 발전 모듈 적용 버전)

import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# --- 경로 설정 및 폰트 설정 ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import save_artifact, get_artifacts_for_project
# gemini_agent에서 필요한 모든 함수를 import
from gemini_agent import generate_performance_report, refine_content

# Matplotlib 한글 폰트 설정
try:
    font_path = fm.findfont("NanumGothic", fallback_to_default=True)
    if font_path:
        plt.rc("font", family="NanumGothic")
    else:
        # NanumGothic이 없을 경우, 시스템의 기본 폰트 사용 시도
        # macOS의 경우 'AppleGothic', Windows의 경우 'Malgun Gothic'
        # 이도 없으면 기본 sans-serif 사용
        if sys.platform == "darwin":
            plt.rc("font", family="AppleGothic")
        elif sys.platform == "win32":
            plt.rc("font", family="Malgun Gothic")
except Exception as e:
    st.warning(f"한글 폰트를 설정하는 중 오류가 발생했습니다: {e}")
plt.rcParams['axes.unicode_minus'] = False


# --- 페이지 기본 설정 ---
st.set_page_config(page_title="성능 검증", layout="wide")
st.title("📊 성능 검증")
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

# --- 2. 성능 지표 입력 ---
st.subheader("Step 1: 성능 지표(Metrics) 입력")
st.info("모델의 성능을 나타내는 주요 지표와 값을 입력하세요. '+' 버튼을 눌러 지표를 추가할 수 있습니다.")

if 'metrics' not in st.session_state:
    st.session_state.metrics = [{"name": "Accuracy", "value": 0.95}]

def add_metric():
    st.session_state.metrics.append({"name": "", "value": 0.0})

def remove_metric(index):
    st.session_state.metrics.pop(index)

for i, metric in enumerate(st.session_state.metrics):
    col1, col2, col3 = st.columns([3, 2, 1])
    st.session_state.metrics[i]['name'] = col1.text_input("지표 이름", value=metric['name'], key=f"perf_metric_name_{i}")
    st.session_state.metrics[i]['value'] = col2.number_input("값", value=metric['value'], key=f"perf_metric_value_{i}", format="%.4f")
    col3.button("삭제", on_click=remove_metric, args=(i,), key=f"perf_remove_metric_{i}", use_container_width=True)

st.button("➕ 지표 추가", on_click=add_metric, use_container_width=True)

# --- 3. AI 리포트 생성 ---
st.markdown("---")
if st.button("🤖 AI로 성능 평가 리포트 생성하기", type="primary", use_container_width=True):
    metrics_dict = {m['name']: m['value'] for m in st.session_state.metrics if m['name']}
    if not metrics_dict:
        st.error("하나 이상의 유효한 성능 지표를 입력해주세요.")
    else:
        with st.spinner("Gemini 에이전트가 성능을 분석하고 리포트를 작성하고 있습니다..."):
            report_text = generate_performance_report(latest_design_doc, metrics_dict)
            st.session_state['generated_perf_report'] = report_text
            st.session_state['current_perf_metrics'] = metrics_dict # 시각화 및 저장을 위해 현재 메트릭 저장
            st.rerun()

# --- 4. 생성 결과 확인, 발전 및 저장 ---
if 'generated_perf_report' in st.session_state:
    st.subheader("Step 2: 생성된 리포트 발전시키기")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.session_state['generated_perf_report'] = st.text_area(
            "내용을 검토하고 직접 수정하거나, 아래 AI 도구를 사용해 보세요.",
            value=st.session_state.generated_perf_report,
            height=400,
            key="perf_report_editor"
        )
    with col2:
        # 시각화
        metrics_to_plot = st.session_state.get('current_perf_metrics', {})
        if metrics_to_plot:
            df_metrics = pd.DataFrame(list(metrics_to_plot.items()), columns=['Metric', 'Value'])
            fig, ax = plt.subplots()
            ax.bar(df_metrics['Metric'], df_metrics['Value'], color='skyblue')
            ax.set_ylabel('Score')
            ax.set_title('Performance Metrics')
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

    st.markdown("---")
    st.write("🤖 **AI 편집 도구모음**")
    current_text = st.session_state.perf_report_editor
    
    custom_instruction = st.text_input("직접 편집 지시하기 (예: 이 리포트 내용을 비전문가도 이해하기 쉽게 다시 써줘)")
    if st.button("실행", disabled=not custom_instruction, key="custom_perf_report"):
        with st.spinner("AI가 당신의 지시를 수행하고 있습니다..."):
            refined_text = refine_content(current_text, custom_instruction)
            st.session_state.generated_perf_report = refined_text
            st.rerun()
            
    st.markdown("---")
    st.subheader("Step 3: 최종본 저장")
    if st.button("💾 이 최종 리포트를 이력으로 저장하기", type="primary", use_container_width=True):
        final_metrics = st.session_state.get('current_perf_metrics', {})
        metrics_md = "\n".join([f"- {name}: {value}" for name, value in final_metrics.items()])
        full_content = f"# 성능 평가 리포트\n\n## 성능 지표\n{metrics_md}\n\n## 종합 분석\n\n{current_text}"

        save_artifact(
            project_id=selected_id,
            stage="VERIFICATION",
            type="PERF_REPORT",
            content=full_content
        )
        st.success("성능 평가 리포트가 이력으로 저장되었습니다.")
        del st.session_state['generated_perf_report']
        del st.session_state['current_perf_metrics']
        st.rerun()

# --- 5. 저장된 이력 ---
st.markdown("---")
st.header("📜 저장된 성능 평가 리포트 이력")
artifacts = get_artifacts_for_project(selected_id, "PERF_REPORT")
if artifacts:
    for i, artifact in enumerate(artifacts):
        with st.expander(f"버전 {len(artifacts) - i} ({artifact['created_at']})"):
            st.markdown(artifact['content'])
else:
    st.info("이 프로젝트에 저장된 성능 평가 리포트가 없습니다.")
