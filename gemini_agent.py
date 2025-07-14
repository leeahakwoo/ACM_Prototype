# gemini_agent.py (타임아웃 설정 및 에러 핸들링 최종 버전)

import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import re
import pandas as pd

# --- API 설정 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# --- 내부 헬퍼 함수 ---
def _call_gemini_with_timeout(prompt: str, timeout_seconds: int = 120) -> str:
    """
    Gemini API 호출을 타임아웃과 함께 실행하고 예외를 처리하는 중앙 함수.
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다. Streamlit Cloud의 'Secrets'에서 API 키를 설정해주세요."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # request_options를 사용하여 타임아웃 설정
        response = model.generate_content(prompt, request_options={"timeout": timeout_seconds})
        return response.text
    except exceptions.DeadlineExceeded:
        st.error(f"오류: API 요청 시간({timeout_seconds}초)이 초과되었습니다. 더 간단한 요청으로 다시 시도하거나, 네트워크 상태를 확인해주세요.")
        return "타임아웃 오류가 발생했습니다."
    except Exception as e:
        # 그 외 모든 API 관련 예외 처리
        st.error(f"LLM 호출 중 예상치 못한 오류가 발생했습니다: {e}")
        return f"오류 발생: {e}"

# --- 각 기능별 에이전트 함수 ---

def generate_problem_definition(prompt_input: dict) -> str:
    """사용자 입력을 바탕으로 문제정의서 내용을 생성합니다."""
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
    return _call_gemini_with_timeout(prompt)

def generate_model_design_doc(problem_def: str, model_type: str) -> str:
    """문제정의서 내용과 모델 유형을 바탕으로 모델 설계서 초안을 생성합니다."""
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
    (선택된 모델 유형에 맞는 구체적인 아키텍처를 제안. 예: BERT 기반 분류기. 전이 학습, 주요 레이어 구성 등 포함)

    ### 3. 입력 및 출력 데이터 명세
    - **입력:** (모델이 받을 데이터의 형태와 예시. 예: `{{'text': '민원 내용 텍스트'}}`)
    - **출력:** (모델이 반환할 데이터의 형태와 예시. 예: `{{'category': '배송 불만', 'confidence': 0.95}}`)

    ### 4. 알고리즘 선정 근거
    (이 문제 해결에 왜 이 모델 아키텍처가 적합한지, 다른 대안과 비교하여 그 정당성을 논리적으로 설명)
    
    (이하 생략)
    """
    return _call_gemini_with_timeout(prompt)

def generate_test_cases(design_doc: str, scenario: str, num_cases: int = 5) -> str:
    """모델 설계서와 시나리오를 바탕으로 단위 테스트 케이스를 생성합니다."""
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
    (이하 생략)
    """
    return _call_gemini_with_timeout(prompt)

def generate_performance_report(design_doc: str, metrics: dict) -> str:
    """모델 설계서와 성능 지표를 바탕으로 성능 평가 리포트를 생성합니다."""
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
    (이하 생략)
    """
    return _call_gemini_with_timeout(prompt)

def generate_trustworthy_report(problem_def: str, fairness_input: str, explainability_input: str, robustness_input: str) -> str:
    """Trustworthy AI 검증 항목들을 바탕으로 종합 리스크 분석 리포트를 생성합니다."""
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
    (이하 생략)
    """
    return _call_gemini_with_timeout(prompt)

def refine_content(original_text: str, instruction: str) -> str:
    """원본 텍스트를 주어진 지시에 따라 수정(Refine)합니다."""
    prompt = f"""
    당신은 뛰어난 문서 편집 전문가(Expert Editor)입니다.
    아래에 주어진 "원본 텍스트"를 "편집 지시"에 따라 수정하여, 완성된 결과물만 응답해주세요.

    ---
    **[편집 지시]**
    {instruction}
    ---
    **[원본 텍스트]**
    {original_text}
    ---
    """
    return _call_gemini_with_timeout(prompt)

def convert_markdown_to_df(markdown_table: str) -> pd.DataFrame:
    """마크다운 테이블 형식의 문자열을 Pandas DataFrame으로 변환합니다."""
    try:
        lines = markdown_table.strip().split('\n')
        # 테이블의 헤더와 데이터를 분리 (구분선 라인 제거)
        header_line = lines[0]
        data_lines = lines[2:]

        # 헤더 파싱
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

def generate_governance_summary(mcp_context: dict, check_results: list) -> str:
    """
    MCP 컨텍스트와 자동 점검 결과를 바탕으로 종합 거버넌스 리포트를 생성합니다.
    """
    if not GEMINI_ENABLED:
        return "오류: Gemini API 키가 설정되지 않았습니다."

    # 분석에 필요한 정보들을 문자열로 변환
    mcp_str = yaml.dump(mcp_context, allow_unicode=True, default_flow_style=False)
    check_str = "\n".join(check_results)

    prompt = f"""
    당신은 AI 거버넌스 및 리스크 관리 최고 책임자(Chief AI Governance Officer)입니다.
    아래 주어진 '모델 컨텍스트(MCP)'와 '자동 점검 결과'를 종합적으로 분석하여, 이 AI 모델의 현재 상태에 대한 상세하고 실행 가능한 '종합 거버넌스 리포트'를 마크다운 형식으로 작성해주세요.

    ---
    **[모델 컨텍스트 (MCP)]**
    ```yaml
    {mcp_str}
    ```
    ---
    **[자동 점검 결과]**
    {check_str}
    ---

    **리포트 작성 지시사항:**

    1.  **Executive Summary:** 현재 모델의 거버넌스 상태를 한 문단으로 요약하고, '배포 가능', '조건부 배포 가능', '배포 위험' 등급 중 하나로 명확히 판단해주세요.
    2.  **주요 리스크 분석:** '자동 점검 결과'에서 "미흡" 또는 "주의"로 표시된 항목들을 중심으로, 이것이 비즈니스, 법률, 윤리적 관점에서 어떤 구체적인 위험을 초래할 수 있는지 심층적으로 분석해주세요.
    3.  **실행 가능한 권고안 (Actionable Recommendations):** 식별된 리스크를 해결하기 위해 개발팀이나 현업 부서가 즉시 수행해야 할 구체적인 조치들을 3~5가지 항목으로 제시해주세요.
    """
    
    # _call_gemini_with_timeout 함수를 사용하여 안정적으로 호출
    return _call_gemini_with_timeout(prompt)
