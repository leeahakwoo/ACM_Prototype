# gemini_agent.py (입력 검증 및 보안 강화 버전)

import google.generativeai as genai
import streamlit as st
import re

# ... (API 설정은 동일)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

def sanitize_input(user_input: str) -> str:
    """간단한 입력값 검증 및 잠재적 위험 문자 제거"""
    if not isinstance(user_input, str):
        return ""
    # 간단한 태그 제거 예시
    sanitized = re.sub(r'<[^>]+>', '', user_input)
    return sanitized

def generate_problem_definition(prompt_input: dict) -> str:
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다."
        
    # 입력 데이터 검증
    use_case = sanitize_input(prompt_input.get("use_case", ""))
    background = sanitize_input(prompt_input.get("background", ""))
    expected_effect = sanitize_input(prompt_input.get("expected_effect", ""))

    if not all([use_case, background, expected_effect]):
        return "오류: 모든 입력 필드를 채워주세요."

    prompt = f"""
    당신은 AI 과제 기획 전문가입니다. 다음 정보를 바탕으로 '문제정의서'를 작성해 주세요.
    - 사용 목적: {use_case}
    - 도입 배경: {background}
    - 기대 효과: {expected_effect}
    (이하 프롬프트 템플릿은 이전과 동일)
    ...
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"LLM 호출 중 오류 발생: {e}")
        return f"오류 발생: {e}"

def generate_model_design_doc(problem_def: str, model_type: str) -> str:
    """
    문제정의서 내용과 모델 유형을 바탕으로 모델 설계서 초안을 생성합니다.
    (설계안의 'B. 모델 설계서 생성 Prompt' 구현)
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다."

    prompt = f"""
    당신은 머신러닝 모델을 설계하는 시니어 AI 아키텍트입니다.
    아래 주어진 '문제 정의'와 '모델 유형'을 바탕으로, 상세하고 전문적인 '모델 설계서'를 마크다운 형식으로 작성해주세요.

    ---
    **[문제 정의]**
    {problem_def}
    ---
    **[사용자가 선택한 모델 유형]**
    {model_type}
    ---

    **요구 형식 (반드시 이 순서와 형식으로 작성):**

    ### 1. 설계 목표
    (주어진 문제 정의를 해결하기 위해, 이 모델이 구체적으로 달성해야 할 기술적 목표를 서술)

    ### 2. 모델 아키텍처
    (선택된 모델 유형에 맞는 구체적인 아키텍처를 제안. 예를 들어 'BERT 기반 분류기' 등. 전이 학습 사용 여부, 주요 레이어 구성 등을 포함)

    ### 3. 입력 및 출력 데이터 명세
    - **입력:** (모델이 받을 데이터의 형태와 예시. 예: `{{'text': '민원 내용 텍스트'}}`)
    - **출력:** (모델이 반환할 데이터의 형태와 예시. 예: `{{'category': '배송 불만', 'confidence': 0.95}}`)

    ### 4. 알고리즘 선정 근거
    (이 문제 해결에 왜 이 모델 아키텍처가 적합한지, 다른 대안과 비교하여 그 정당성을 논리적으로 설명)

    ### 5. 주요 하이퍼파라미터 및 학습 전략
    (해당 모델의 일반적인 주요 하이퍼파라미터와 그 추천값을 나열하고, 간략한 학습 전략을 제안)

    ### 6. 성능 평가 지표
    (이 모델의 성능을 측정하기 위한 주요 지표(예: Accuracy, F1-score, ROC-AUC 등)를 명시)
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"LLM 호출 중 오류 발생: {e}")
        return f"오류 발생: {e}"

# gemini_agent.py 에 추가할 내용
import pandas as pd

def generate_test_cases(design_doc: str, scenario: str, num_cases: int = 5) -> str:
    """
    모델 설계서와 시나리오를 바탕으로 단위 테스트 케이스를 생성합니다.
    (설계안의 'C. 단위 테스트케이스 생성 Prompt' 구현)
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다."

    prompt = f"""
    당신은 QA(Quality Assurance) 전문가입니다.
    아래 주어진 '모델 설계서' 내용과 '테스트 시나리오'를 바탕으로, 모델의 기능을 검증하기 위한 구체적인 단위 테스트 케이스 {num_cases}개를 생성해주세요.
    결과는 반드시 마크다운 테이블 형식으로, "TC_ID", "테스트 설명", "입력값 (JSON)", "예상 출력값 (JSON)" 컬럼을 포함해야 합니다.

    ---
    **[모델 설계서]**
    {design_doc}
    ---
    **[테스트 시나리오]**
    {scenario}
    ---

    **요구 형식 (마크다운 테이블):**

    | TC_ID | 테스트 설명 | 입력값 (JSON) | 예상 출력값 (JSON) |
    |---|---|---|---|
    | TC-001 | ... | ... | ... |
    | TC-002 | ... | ... | ... |
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"LLM 호출 중 오류 발생: {e}")
        return f"오류 발생: {e}"

def convert_markdown_to_df(markdown_table: str) -> pd.DataFrame:
    """마크다운 테이블 형식의 문자열을 Pandas DataFrame으로 변환합니다."""
    try:
        # 테이블의 헤더와 데이터를 분리
        lines = markdown_table.strip().split('\n')
        header_line = lines[0]
        data_lines = lines[2:]

        # 헤더 파싱 (양 끝의 '|' 제거 및 공백 제거)
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # 데이터 파싱
        data = []
        for line in data_lines:
            row = [d.strip() for d in line.split('|') if d.strip()]
            if len(row) == len(headers):
                data.append(row)
        
        df = pd.DataFrame(data, columns=headers)
        return df
    except Exception as e:
        print(f"DataFrame 변환 오류: {e}")
        return pd.DataFrame()

# gemini_agent.py 에 추가할 내용

def generate_performance_report(design_doc: str, metrics: dict) -> str:
    """
    모델 설계서와 성능 지표를 바탕으로 성능 평가 리포트를 생성합니다.
    (설계안의 'D. 성능 평가 리포트 생성 Prompt' 구현)
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다."
    
    # metrics 딕셔너리를 문자열로 변환
    metrics_str = "\n".join([f"- {key}: {value}" for key, value in metrics.items()])

    prompt = f"""
    당신은 데이터 과학자이자 성능 분석 전문가입니다.
    아래 주어진 '모델 설계서'의 내용과 실제 '성능 평가 결과'를 종합하여, 상세하고 전문적인 '성능 평가 리포트'를 마크다운 형식으로 작성해주세요.

    ---
    **[모델 설계서 요약]**
    {design_doc}
    ---
    **[성능 평가 결과]**
    {metrics_str}
    ---

    **요구 형식 (반드시 이 순서와 형식으로 작성):**

    ### 1. 총평 (Executive Summary)
    (모델의 전반적인 성능을 요약하고, 설계 단계에서 목표했던 성능 수준을 달성했는지 평가)

    ### 2. 주요 성능 지표 분석
    (각 성능 지표(예: Precision, Recall)의 수치가 비즈니스 관점에서 구체적으로 무엇을 의미하는지 해석. 모델의 강점과 약점을 명확히 기술)

    ### 3. 개선이 필요한 지점 및 제언
    (성능 분석 결과를 바탕으로 모델의 성능을 향상시키기 위한 구체적인 액션 아이템 제안. 예: 데이터 추가 수집, 특정 하이퍼파라미터 튜닝, 다른 알고리즘 시도 등)
    
    ### 4. 사용 시 유의사항
    (이 모델을 실제 운영 환경에 배포할 때 발생할 수 있는 잠재적 리스크나 반드시 모니터링해야 할 사항을 제시)
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"LLM 호출 중 오류 발생: {e}")
        return f"오류 발생: {e}"

# gemini_agent.py 에 추가할 내용

def generate_trustworthy_report(problem_def: str, fairness_input: str, explainability_input: str, robustness_input: str) -> str:
    """
    Trustworthy AI 검증 항목들을 바탕으로 종합 리스크 분석 리포트를 생성합니다.
    (설계안의 거버넌스 검토 항목 구현)
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다."

    prompt = f"""
    당신은 AI 거버넌스 및 윤리 리스크 전문 컨설턴트입니다.
    아래 주어진 '프로젝트 개요'와 '신뢰성 검증 결과'를 종합하여, 이 AI 모델의 잠재적 리스크와 규정 준수 관련 사항을 분석하는 'Trustworthy AI 검증 리포트'를 마크다운 형식으로 작성해주세요.

    ---
    **[프로젝트 개요]**
    {problem_def}
    ---
    **[신뢰성 검증 결과]**
    - **공정성 (Fairness):** {fairness_input}
    - **설명가능성 (Explainability, XAI):** {explainability_input}
    - **강건성 (Robustness):** {robustness_input}
    ---

    **요구 형식 (반드시 이 순서와 형식으로 작성):**

    ### 1. 종합 평가 (Overall Assessment)
    (입력된 검증 결과를 바탕으로 모델의 전반적인 신뢰성 수준을 평가. 고위험 AI 분류 가능성이 있는지 여부를 포함)

    ### 2. 항목별 상세 분석 및 잠재적 리스크
    - **공정성 리스크:** 현재 검증 결과가 불충분할 경우 발생할 수 있는 사회적, 법적 리스크를 분석.
    - **설명가능성 리스크:** 모델의 결정 과정을 설명할 수 없을 때 발생할 수 있는 문제점(예: 사용자 불신, 디버깅의 어려움)을 지적.
    - **강건성 리스크:** 예상치 못한 입력이나 데이터 변화에 모델이 어떻게 오작동할 수 있는지 구체적인 시나리오를 제시.

    ### 3. 규정 준수 및 완화 조치 제언
    (EU AI Act, ISO 42001 등 주요 AI 규제 프레임워크 관점에서 추가적으로 필요한 검증 항목이나 문서화가 필요한 사항을 제안하고, 발견된 리스크를 완화하기 위한 구체적인 기술적/정책적 조치를 권고)
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"LLM 호출 중 오류 발생: {e}")
        return f"오류 발생: {e}"
