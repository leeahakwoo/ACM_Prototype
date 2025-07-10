# your_mcp_project/pages/1_📝_문제_정의서.py

import streamlit as st

# -------------------- 페이지 설정 및 초기화 --------------------

# st.set_page_config()는 메인 app.py에서만 호출해야 합니다.
# 여기서는 페이지 제목만 설정합니다.
st.title("📝 문제 정의서 작성")
st.markdown("---")

# session_state에 'problem_definition'이 없는 경우를 대비한 방어 코드
# app.py에서 이미 초기화했지만, 페이지 단독 실행 등 예외 상황을 방지합니다.
if 'problem_definition' not in st.session_state:
    st.session_state['problem_definition'] = {
        "project_name": "",
        "project_goal": "",
        "problem_background": "",
        "expected_output": ""
    }

# -------------------- 입력 폼 --------------------

st.header("1. 프로젝트 개요")
st.info("AI 프로젝트의 기본적인 정보와 목표를 명확히 정의합니다.", icon="ℹ️")

# st.form을 사용하여 여러 입력 위젯을 그룹화하고, '저장' 버튼을 누를 때 한 번에 처리합니다.
# 이렇게 하면 각 위젯을 조작할 때마다 페이지가 새로고침되는 것을 방지하여 사용자 경험을 향상시킵니다.
with st.form("problem_definition_form"):
    # session_state에 저장된 값을 기본값(value)으로 사용합니다.
    # 사용자가 다른 페이지에 다녀와도 입력했던 내용이 그대로 유지됩니다.
    project_name = st.text_input(
        "프로젝트 이름",
        value=st.session_state.problem_definition.get("project_name", ""),
        help="예: 고객 이탈 예측 AI 모델"
    )

    project_goal = st.text_area(
        "프로젝트의 최종 목표",
        value=st.session_state.problem_definition.get("project_goal", ""),
        height=100,
        help="이 프로젝트를 통해 달성하고자 하는 비즈니스 또는 기술적 목표를 구체적으로 작성합니다."
    )

    problem_background = st.text_area(
        "문제 배경 및 필요성",
        value=st.session_state.problem_definition.get("problem_background", ""),
        height=200,
        help="어떤 문제를 해결하기 위해 이 프로젝트가 필요한지, 현재 상황과 문제점을 상세히 기술합니다."
    )
    
    expected_output = st.text_area(
        "핵심 결과물 (Key Deliverables)",
        value=st.session_state.problem_definition.get("expected_output", ""),
        height=100,
        help="프로젝트 완료 시 나와야 하는 최종 결과물을 명시합니다. 예: 이탈 가능성 점수(0-1)를 예측하는 API, 주간 리포트 대시보드"
    )

    # 폼 제출 버튼
    submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        # '저장하기' 버튼이 눌리면, form 내부의 위젯들의 현재 값을 session_state에 업데이트합니다.
        st.session_state.problem_definition['project_name'] = project_name
        st.session_state.problem_definition['project_goal'] = project_goal
        st.session_state.problem_definition['problem_background'] = problem_background
        st.session_state.problem_definition['expected_output'] = expected_output

        st.success("문제 정의서 내용이 성공적으로 저장되었습니다!")
        st.balloons() # 저장 성공을 축하하는 작은 애니메이션 효과

# -------------------- 저장된 데이터 확인 --------------------

st.markdown("---")
st.header("2. 현재 저장된 내용 확인")

# st.expander를 사용하여 깔끔하게 표시
with st.expander("저장된 문제 정의서 보기"):
    # session_state에 값이 있는지 확인 후 표시
    if any(st.session_state.problem_definition.values()):
        st.json(st.session_state.problem_definition)
    else:
        st.warning("아직 저장된 내용이 없습니다. 위의 폼을 작성하고 '저장하기' 버튼을 눌러주세요.")

st.info("내용을 모두 작성하고 저장하셨다면, 왼쪽 사이드바에서 다음 단계인 **'🤖 모델 정의서'** 페이지로 이동하세요.", icon="👉")
