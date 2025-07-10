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
