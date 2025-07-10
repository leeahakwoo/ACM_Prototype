# your_mcp_project/pages/2_🤖_모델_정의서.py

import streamlit as st

# -------------------- 페이지 설정 및 초기화 --------------------

st.title("🤖 모델 정의서 작성")
st.markdown("---")

# session_state 초기화 방어 코드 (app.py에서 이미 수행)
if 'problem_definition' not in st.session_state:
    st.warning("먼저 '📝 문제 정의서' 페이지에서 프로젝트 개요를 작성해주세요.")
    st.stop() # 페이지 실행 중단

if 'model_spec' not in st.session_state:
    st.session_state['model_spec'] = {
        "model_name": "",
        "model_type": "분류", # 기본값 설정
        "key_features": "",
        "hyperparameters": ""
    }

# -------------------- 문제 정의서 내용 확인 --------------------

st.header("1. 프로젝트 개요 확인")
with st.expander("저장된 문제 정의서 보기", expanded=False):
    # '문제 정의서'에서 저장된 값이 있는지 확인
    if st.session_state.problem_definition.get("project_name"):
        st.success("문제 정의서가 로드되었습니다.")
        # 주요 정보만 간략히 표시
        st.markdown(f"**프로젝트 이름:** {st.session_state.problem_definition.get('project_name')}")
        st.markdown(f"**프로젝트 목표:** {st.session_state.problem_definition.get('project_goal')}")
    else:
        st.error("오류: '📝 문제 정의서'가 작성되지 않았습니다. 이전 페이지로 돌아가 내용을 먼저 저장해주세요.")
        st.stop() # 필수 정보가 없으므로 페이지 실행 중단

# -------------------- 모델 정보 입력 폼 --------------------

st.header("2. 모델 사양 정의")
st.info("개발할 AI 모델의 이름, 종류, 주요 변수 및 하이퍼파라미터를 구체적으로 정의합니다.", icon="ℹ️")

with st.form("model_spec_form"):
    # session_state에 저장된 값을 기본값(value)으로 사용
    model_name = st.text_input(
        "모델 이름",
        value=st.session_state.model_spec.get("model_name", ""),
        help="예: XGBoost 기반 이탈 예측 모델 v1.0"
    )

    model_type = st.selectbox(
        "모델 유형",
        ("분류", "회귀", "클러스터링", "자연어 처리", "이미지 인식", "기타"),
        index=("분류", "회귀", "클러스터링", "자연어 처리", "이미지 인식", "기타").index(st.session_state.model_spec.get("model_type", "분류")),
        help="개발할 모델의 주요 태스크를 선택합니다."
    )

    key_features = st.text_area(
        "주요 피처(입력 변수)",
        value=st.session_state.model_spec.get("key_features", ""),
        height=150,
        help="모델 학습에 사용될 핵심적인 입력 변수(피처)들을 나열합니다. 예: 최근 6개월간 구매 횟수, 평균 구매 금액, 마지막 접속일 등"
    )

    hyperparameters = st.text_area(
        "주요 하이퍼파라미터",
        value=st.session_state.model_spec.get("hyperparameters", ""),
        height=200,
        help="모델의 성능에 영향을 미치는 주요 하이퍼파라미터와 그 설정값을 기술합니다. 예:\nlearning_rate: 0.01\nn_estimators: 200\nmax_depth: 5"
    )

    # 폼 제출 버튼
    submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        # '저장하기' 버튼이 눌리면, form 내부의 위젯들의 현재 값을 session_state에 업데이트합니다.
        st.session_state.model_spec['model_name'] = model_name
        st.session_state.model_spec['model_type'] = model_type
        st.session_state.model_spec['key_features'] = key_features
        st.session_state.model_spec['hyperparameters'] = hyperparameters

        st.success("모델 정의서 내용이 성공적으로 저장되었습니다!")

# -------------------- 저장된 데이터 확인 --------------------

st.markdown("---")
st.header("3. 현재 저장된 내용 확인")

with st.expander("저장된 모델 정의서 보기"):
    if any(st.session_state.model_spec.values()):
        st.json(st.session_state.model_spec)
    else:
        st.warning("아직 저장된 내용이 없습니다. 위의 폼을 작성하고 '저장하기' 버튼을 눌러주세요.")

st.info("내용을 모두 작성하고 저장하셨다면, 왼쪽 사이드바에서 다음 단계인 **'📊 모델 검증'** 페이지로 이동하세요.", icon="👉")
