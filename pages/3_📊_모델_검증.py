# your_mcp_project/pages/3_📊_모델_검증.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# 한글 폰트 설정 (matplotlib)
# Streamlit Cloud에서는 Clear-sans 폰트가 기본적으로 설치되어 있어 깨짐 현상이 덜하지만,
# 로컬이나 다른 환경에서는 폰트 설정이 필요할 수 있습니다.
# 여기서는 폰트 매니저를 사용하여 시스템에 설치된 한글 폰트를 찾도록 시도합니다.
try:
    import matplotlib.font_manager as fm
    # 시스템에 설치된 나눔고딕 폰트 경로를 직접 지정하거나, findfont로 찾기
    font_path = fm.findfont('NanumGothic', fallback_to_default=True)
    if font_path:
        plt.rc('font', family='NanumGothic')
    else:
        # NanumGothic이 없을 경우, 시스템의 기본 sans-serif 폰트 사용
        plt.rc('font', family='sans-serif')
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
except:
    st.warning("한글 폰트를 찾을 수 없어 일부 차트의 글자가 깨질 수 있습니다.")


# -------------------- 페이지 설정 및 초기화 --------------------

st.set_page_config(page_title="모델 검증 결과", layout="wide") # 이 페이지는 넓게 사용
st.title("📊 모델 검증 및 최종 리포트")
st.markdown("---")

# session_state 의존성 확인
if 'problem_definition' not in st.session_state or not st.session_state.problem_definition.get('project_name'):
    st.error("먼저 '📝 문제 정의서' 페이지를 작성해주세요.")
    st.stop()
if 'model_spec' not in st.session_state or not st.session_state.model_spec.get('model_name'):
    st.error("먼저 '🤖 모델 정의서' 페이지를 작성해주세요.")
    st.stop()
if 'model_validation' not in st.session_state:
    st.session_state.model_validation = {
        "validation_metrics": {},
        "summary": ""
    }

# -------------------- 종합 정보 요약 --------------------

st.header("📄 최종 문서 요약")
st.info("이전 단계에서 작성한 내용을 바탕으로 생성된 최종 문서입니다.")

with st.container(border=True):
    st.subheader("1. 문제 정의")
    prob_def = st.session_state.problem_definition
    st.markdown(f"**- 프로젝트 명:** {prob_def.get('project_name', 'N/A')}")
    st.markdown(f"**- 프로젝트 목표:** {prob_def.get('project_goal', 'N/A')}")

    st.subheader("2. 모델 정의")
    model_spec = st.session_state.model_spec
    st.markdown(f"**- 모델 명:** {model_spec.get('model_name', 'N/A')}")
    st.markdown(f"**- 모델 유형:** {model_spec.get('model_type', 'N/A')}")
    with st.expander("모델 상세 정보 보기"):
        st.markdown("**주요 피처(입력 변수):**")
        st.text(model_spec.get('key_features', 'N/A'))
        st.markdown("**주요 하이퍼파라미터:**")
        st.text(model_spec.get('hyperparameters', 'N/A'))


st.markdown("---")

# -------------------- 모델 성능 지표 입력 및 시각화 --------------------

st.header("3. 모델 성능 검증")
col1, col2 = st.columns([1, 2]) # 컬럼 비율 1:2로 분할

with col1:
    st.subheader("성능 지표 입력")
    # 모델 유형에 따라 다른 성능 지표 입력 필드를 보여줍니다.
    model_type = st.session_state.model_spec.get("model_type")
    
    with st.form("metrics_form"):
        metrics = {}
        if model_type == "분류":
            metrics['정확도 (Accuracy)'] = st.number_input("정확도 (Accuracy)", min_value=0.0, max_value=1.0, value=st.session_state.model_validation.get('validation_metrics', {}).get('정확도 (Accuracy)', 0.92), format="%.4f")
            metrics['정밀도 (Precision)'] = st.number_input("정밀도 (Precision)", min_value=0.0, max_value=1.0, value=st.session_state.model_validation.get('validation_metrics', {}).get('정밀도 (Precision)', 0.88), format="%.4f")
            metrics['재현율 (Recall)'] = st.number_input("재현율 (Recall)", min_value=0.0, max_value=1.0, value=st.session_state.model_validation.get('validation_metrics', {}).get('재현율 (Recall)', 0.90), format="%.4f")
            metrics['F1 점수 (F1 Score)'] = st.number_input("F1 점수 (F1 Score)", min_value=0.0, max_value=1.0, value=st.session_state.model_validation.get('validation_metrics', {}).get('F1 점수 (F1 Score)', 0.89), format="%.4f")
        elif model_type == "회귀":
            metrics['MSE'] = st.number_input("MSE (Mean Squared Error)", value=st.session_state.model_validation.get('validation_metrics', {}).get('MSE', 15.7), format="%.4f")
            metrics['RMSE'] = st.number_input("RMSE (Root Mean Squared Error)", value=st.session_state.model_validation.get('validation_metrics', {}).get('RMSE', 3.96), format="%.4f")
            metrics['R²'] = st.number_input("R² (R-squared)", value=st.session_state.model_validation.get('validation_metrics', {}).get('R²', 0.85), format="%.4f")
        else:
            st.info("현재 모델 유형에 대한 기본 성능 지표가 없습니다. 직접 추가해주세요.")
            # 향후 다른 모델 유형에 대한 지표 추가 가능
            
        summary_text = st.text_area(
            "성능 검증 결과 요약",
            height=150,
            value=st.session_state.model_validation.get("summary", "테스트 데이터셋에서 안정적인 성능을 보임. 특히 재현율이 높아 이탈 고객을 놓치지 않는 데 강점이 있음."),
            help="모델 성능에 대한 종합적인 평가와 결론을 작성합니다."
        )

        submitted = st.form_submit_button("📊 결과 저장 및 차트 생성")

        if submitted:
            st.session_state.model_validation['validation_metrics'] = metrics
            st.session_state.model_validation['summary'] = summary_text
            st.success("모델 검증 결과가 저장되었습니다.")

with col2:
    st.subheader("성능 지표 시각화")
    if 'validation_metrics' in st.session_state.model_validation and st.session_state.model_validation['validation_metrics']:
        metrics_data = st.session_state.model_validation['validation_metrics']
        
        # 데이터프레임으로 변환
        df_metrics = pd.DataFrame(list(metrics_data.items()), columns=['Metric', 'Value'])
        
        # 막대 그래프 생성 (matplotlib)
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(df_metrics['Metric'], df_metrics['Value'], color=plt.cm.viridis(df_metrics['Value'] / df_metrics['Value'].max()))
        ax.set_title(f'{model_spec.get("model_name")} 성능 지표', fontsize=15)
        ax.set_ylabel('값(Value)', fontsize=12)
        ax.set_ylim(0, max(1.0, df_metrics['Value'].max() * 1.2)) # Y축 범위 설정 (최소 1.0)
        
        # 막대 위에 값 표시
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f'{yval:.3f}', ha='center', va='bottom')

        st.pyplot(fig)
        
        st.markdown("**종합 의견:**")
        st.write(st.session_state.model_validation.get("summary", "요약 내용이 없습니다."))
        
    else:
        st.info("왼쪽에서 성능 지표를 입력하고 '결과 저장 및 차트 생성' 버튼을 클릭하세요.")


st.markdown("---")
st.success("🎉 모든 문서 작성이 완료되었습니다! 이 페이지를 공유하거나 인쇄하여 최종 리포트로 활용할 수 있습니다.")
