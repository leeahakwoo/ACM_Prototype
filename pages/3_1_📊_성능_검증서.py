# your_mcp_project/pages/3_1_📊_성능_검증서.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# 한글 폰트 설정 (matplotlib)
try:
    import matplotlib.font_manager as fm
    font_path = fm.findfont('NanumGothic', fallback_to_default=True)
    if font_path:
        plt.rc('font', family='NanumGothic')
    else:
        plt.rc('font', family='sans-serif')
    plt.rcParams['axes.unicode_minus'] = False
except:
    st.warning("한글 폰트를 찾을 수 없어 일부 차트의 글자가 깨질 수 있습니다.")

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("📊 성능 검증서 작성")
st.markdown("---")

# session_state 의존성 확인
if 'model_spec' not in st.session_state or not st.session_state.model_spec.get('model_name'):
    st.error("먼저 '2_2_🤖 모델 정의서' 페이지를 작성해주세요.")
    st.stop()
if 'model_validation' not in st.session_state:
    st.session_state['model_validation'] = {
        "validation_metrics": {},
        "summary": ""
    }

# -------------------- 성능 지표 입력 --------------------
st.header("1. 모델 성능 지표 입력")
st.info("모델 유형에 맞는 성능 지표를 입력하고 '결과 저장 및 분석 시작' 버튼을 눌러주세요.")

col1, col2 = st.columns(2)

with col1:
    with st.form("metrics_form"):
        model_type = st.session_state.model_spec.get("model_type")
        metrics = {}
        
        # 모델 유형에 따른 동적 입력 필드
        if model_type == "분류":
            metrics['정확도 (Accuracy)'] = st.number_input("정확도 (Accuracy)", 0.0, 1.0, 0.92, "%.4f")
            metrics['정밀도 (Precision)'] = st.number_input("정밀도 (Precision)", 0.0, 1.0, 0.88, "%.4f")
            metrics['재현율 (Recall)'] = st.number_input("재현율 (Recall)", 0.0, 1.0, 0.90, "%.4f")
            metrics['F1 점수 (F1 Score)'] = st.number_input("F1 점수 (F1 Score)", 0.0, 1.0, 0.89, "%.4f")
        elif model_type == "회귀":
            metrics['MSE'] = st.number_input("MSE", value=15.7, format="%.4f")
            metrics['RMSE'] = st.number_input("RMSE", value=3.96, format="%.4f")
            metrics['R²'] = st.number_input("R²", value=0.85, format="%.4f")
        elif model_type == "이미지 인식":
            metrics['정확도 (Accuracy)'] = st.number_input("정확도 (Accuracy)", 0.0, 1.0, 0.965, "%.4f")
            metrics['민감도 (Recall/Sensitivity)'] = st.number_input("민감도 (Recall/Sensitivity)", 0.0, 1.0, 0.972, "%.4f")
            metrics['특이도 (Specificity)'] = st.number_input("특이도 (Specificity)", 0.0, 1.0, 0.958, "%.4f")
            metrics['AUC'] = st.number_input("AUC", 0.0, 1.0, 0.981, "%.4f")
        else:
            st.info("현재 모델 유형에 대한 기본 지표가 없습니다. 수동으로 요약해주세요.")

        submitted = st.form_submit_button("💾 결과 저장 및 AI 분석 시작")

        if submitted:
            st.session_state.model_validation['validation_metrics'] = metrics
            st.success("성능 지표가 저장되었습니다. AI가 종합 평가를 생성합니다.")

# -------------------- AI 기반 종합 평가 및 시각화 --------------------
with col2:
    st.header("2. 종합 평가 및 시각화")
    if 'validation_metrics' in st.session_state.model_validation and st.session_state.model_validation['validation_metrics']:
        metrics_data = st.session_state.model_validation['validation_metrics']
        
        # 성능 지표 시각화
        st.subheader("성능 지표 시각화")
        df_metrics = pd.DataFrame(list(metrics_data.items()), columns=['Metric', 'Value'])
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(df_metrics['Metric'], df_metrics['Value'], color=plt.cm.viridis(df_metrics['Value'] / max(1.0, df_metrics['Value'].max())))
        ax.set_title(f'{st.session_state.model_spec.get("model_name")} 성능', fontsize=12)
        ax.set_ylim(0, max(1.0, df_metrics['Value'].max() * 1.2))
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f'{yval:.3f}', ha='center', va='bottom')
        plt.xticks(rotation=30, ha='right')
        st.pyplot(fig)

        # AI 종합 평가 생성
        st.subheader("🤖 AI 종합 평가")
        if GEMINI_ENABLED:
            with st.spinner("Gemini가 성능 지표를 분석하고 종합 평가를 작성 중입니다..."):
                problem_goal = st.session_state.problem_definition.get('project_goal', 'N/A')
                model_type = st.session_state.model_spec.get('model_type', 'N/A')
                metrics_str = "\n".join([f"- {k}: {v:.4f}" for k, v in metrics_data.items()])

                prompt = f"""
                당신은 데이터 분석 결과를 보고하는 시니어 분석가입니다.
                아래 주어진 프로젝트 목표와 모델 성능 지표를 바탕으로, 모델의 성능에 대한 종합적인 평가 리포트를 작성해주세요.
                전문가의 시선에서 각 지표의 의미를 해석하고, 모델의 강점과 약점, 그리고 개선 방향을 포함하여 분석해주세요.

                **프로젝트 목표:** {problem_goal}
                **모델 유형:** {model_type}
                **성능 지표:**
                {metrics_str}

                **리포트 형식:**
                1.  **총평:** 모델 성능에 대한 전반적인 요약.
                2.  **세부 분석:** 각 성능 지표가 비즈니스 관점에서 무엇을 의미하는지 해석.
                3.  **결론 및 제언:** 모델의 상용화 가능성 및 추가적으로 개선할 점 제안.
                """
                
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    st.session_state.model_validation['summary'] = response.text
                except Exception as e:
                    st.error(f"AI 종합 평가 생성에 실패했습니다: {e}")
                    st.session_state.model_validation['summary'] = "AI 요약 생성 중 오류 발생."

        # 생성된 요약 표시
        st.markdown(st.session_state.model_validation.get('summary', "왼쪽에서 지표를 입력하고 버튼을 클릭하면 AI가 종합 평가를 생성합니다."))
    else:
        st.info("왼쪽에서 성능 지표를 입력하고 '결과 저장 및 AI 분석 시작' 버튼을 클릭해주세요.")

st.markdown("---")
st.info("다음 단계인 **'🛡️ Trustworthy 검증서'** 페이지로 이동하여 모델의 신뢰성을 검증하세요.", icon="👉")
