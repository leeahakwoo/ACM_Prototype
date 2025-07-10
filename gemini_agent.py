# gemini_agent.py

import google.generativeai as genai
import streamlit as st

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

def generate_problem_definition(prompt_input: dict) -> str:
    """
    사용자 입력을 바탕으로 문제정의서 내용을 생성합니다.
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다. Streamlit Cloud의 'Secrets'에서 API 키를 설정해주세요."
        
    use_case = prompt_input.get("use_case", "정의되지 않음")
    background = prompt_input.get("background", "정의되지 않음")
    expected_effect = prompt_input.get("expected_effect", "정의되지 않음")

    prompt = f"""
    당신은 AI 과제를 기획하는 전문 기획자입니다. 다음 핵심 정보를 바탕으로 체계적인 '문제정의서'를 마크다운 형식으로 작성해 주세요.
    각 항목은 전문적이고 구체적인 내용으로 서술해야 합니다.

    - **사용 목적:** {use_case}
    - **도입 배경:** {background}
    - **기대 효과:** {expected_effect}

    **요구 형식 (반드시 이 순서와 형식으로 작성):**
    
    ### 1. 문제 배경
    (도입 배경을 바탕으로, 현재 상황의 문제점과 이 과제가 왜 필요한지 상세히 서술)

    ### 2. 해결하고자 하는 문제
    (위 배경에서 도출된, AI 모델이 구체적으로 해결해야 할 핵심 문제를 명확히 정의)
    
    ### 3. AI 모델의 역할
    (사용 목적을 바탕으로, AI 모델이 어떤 입력을 받아 어떤 출력을 내보내야 하는지 정의)

    ### 4. 기대 효과
    (기대 효과를 정성적/정량적 관점에서 상세하게 기술)
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"LLM 호출 중 오류 발생: {e}"
