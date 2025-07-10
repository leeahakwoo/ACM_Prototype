# your_mcp_project/pages/3_2_🛡️_Trustworthy_검증서.py

import streamlit as st
import google.generativeai as genai

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("🛡️ Trustworthy AI 검증서 작성")
st.markdown("---")
st.info("""
**Trustworthy AI(신뢰할 수 있는 AI)**는 모델이 단순히 높은 성능을 내는 것을 넘어, 공정성, 설명가능성, 강건성 등 사회적/윤리적 요구사항을 만족하는지 검증하는 과정입니다.
- **공정성 (Fairness):** 특정 그룹(성별, 인종 등)에 편향된 예측을 하지 않는가?
- **설명가능성 (Explainability, XAI):** 모델이 왜 그런 예측을 했는지 인간이 이해할 수 있는가?
- **강건성 (Robustness):** 노이즈나 예상치 못한 입력에도 모델이 안정적으로 동작하는가?
""")

# session_state 의존성 확인
if 'model_spec' not in st.session_state or not st.session_state.model_spec.get('model_name'):
    st.error("먼저 '2_2_🤖 모델 정의서' 페이지를 작성해주세요.")
    st.stop()

# Trustworthy 검증서 session_state 초기화
if 'trustworthy_validation' not in st.session_state:
    st.session_state['trustworthy_validation'] = {
        "fairness_result": "",
        "explainability_result": "",
        "robustness_result": "",
        "overall_summary": ""
    }

# -------------------- 검증 결과 입력 폼 --------------------
st.header("1. 신뢰성 검증 결과 입력")
st.markdown("각 항목에 대한 검증 방법과 결과를 자유롭게 기술해주세요.")

with st.form("trustworthy_form"):
    # session_state에 저장된 값을 기본값으로 사용
    fairness_result = st.text_area(
        "공정성(Fairness) 검증",
        value=st.session_state.trustworthy_validation.get("fairness_result", ""),
        height=150,
        help="예: 성별에 따른 예측값 차이 분석 결과, 유의미한 차이 없음 (Demographic Parity: 0.05 이하)"
    )

    explainability_result = st.text_area(
        "설명가능성(Explainability) 검증",
        value=st.session_state.trustworthy_validation.get("explainability_result", ""),
        height=150,
        help="예: SHAP 분석 결과, '최근 3개월 결제액'과 '로그인 빈도'가 예측에 가장 큰 영향을 미치는 것으로 확인됨."
    )

    robustness_result = st.text_area(
        "강건성(Robustness) 검증",
        value=st.session_state.trustworthy_validation.get("robustness_result", ""),
        height=150,
        help="예: 입력 데이터에 5%의 랜덤 노이즈를 추가했을 때, 모델 성능(Accuracy)이 2%p 이내로 하락하여 안정성을 확인함."
    )

    submitted = st.form_submit_button("💾 결과 저장 및 AI 종합 평가 시작")

    if submitted:
        st.session_state.trustworthy_validation['fairness_result'] = fairness_result
        st.session_state.trustworthy_validation['explainability_result'] = explainability_result
        st.session_state.trustworthy_validation['robustness_result'] = robustness_result
        st.success("신뢰성 검증 결과가 저장되었습니다. AI가 종합 평가를 생성합니다.")

# -------------------- AI 기반 종합 평가 --------------------
st.header("2. 🤖 AI 종합 평가")

# 저장된 검증 결과가 있을 때만 AI 평가 버튼을 보여줌
if any(st.session_state.trustworthy_validation.values()):
    if GEMINI_ENABLED:
        with st.spinner("Gemini가 신뢰성 검증 결과를 바탕으로 종합 평가를 작성 중입니다..."):
            
            # 프롬프트에 모든 관련 정보 포함
            fairness = st.session_state.trustworthy_validation.get('fairness_result')
            explainability = st.session_state.trustworthy_validation.get('explainability_result')
            robustness = st.session_state.trustworthy_validation.get('robustness_result')
            problem_goal = st.session_state.problem_definition.get('project_goal', 'N/A')

            prompt = f"""
            당신은 AI 윤리 및 신뢰성 전문가입니다.
            아래 주어진 프로젝트 목표와 신뢰성 검증 결과를 바탕으로, 이 모델의 'Trustworthy AI' 수준에 대한 종합적인 평가 리포트를 작성해주세요.
            전문가의 시선에서 각 검증 결과의 의미를 해석하고, 모델 배포 시 고려해야 할 잠재적 위험과 권장 사항을 포함하여 분석해주세요.

            **프로젝트 목표:** {problem_goal}

            **[신뢰성 검증 결과]**
            - **공정성:** {fairness}
            - **설명가능성:** {explainability}
            - **강건성:** {robustness}

            **리포트 형식:**
            1.  **총평:** 신뢰성 수준에 대한 전반적인 요약.
            2.  **세부 분석:** 각 검증 결과(공정성, 설명가능성, 강건성)가 실제 서비스에 어떤 영향을 미칠 수 있는지 분석.
            3.  **잠재적 위험 및 권장 사항:** 모델 배포 전/후에 모니터링해야 할 사항이나 추가적으로 검토해야 할 윤리적 이슈를 제안.
            """
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.session_state.trustworthy_validation['overall_summary'] = response.text
            except Exception as e:
                st.error(f"AI 종합 평가 생성에 실패했습니다: {e}")
                st.session_state.trustworthy_validation['overall_summary'] = "AI 요약 생성 중 오류 발생."
    
    # 생성된 요약 표시
    st.markdown(st.session_state.trustworthy_validation.get('overall_summary', "결과를 저장하면 AI가 종합 평가를 생성합니다."))
else:
    st.info("위 폼에 각 항목의 검증 결과를 입력하고 '결과 저장 및 AI 종합 평가 시작' 버튼을 눌러주세요.")

st.markdown("---")
st.success("🎉 모든 문서 작성이 완료되었습니다! 이제 첫 페이지인 '프로젝트 대시보드'로 돌아가 전체 진행 상황을 확인해보세요.")
