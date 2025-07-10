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
