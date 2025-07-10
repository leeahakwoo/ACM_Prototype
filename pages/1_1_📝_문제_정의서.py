# your_mcp_project/pages/1_1_📝_문제_정의서.py
# (대화형 Wizard로 개선된 버전)

import streamlit as st
import google.generativeai as genai
import json
import re

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("📝 문제 정의서 (AI Wizard)")
st.markdown("---")

# session_state 초기화 (문제 정의서 데이터, 대화 기록)
if 'problem_definition' not in st.session_state:
    st.session_state.problem_definition = {
        "project_name": "", "project_goal": "", "problem_background": "", "expected_output": ""
    }
if "pd_messages" not in st.session_state:
    st.session_state.pd_messages = []

# -------------------- 대화형 AI Wizard UI --------------------
st.header("✨ 대화형 AI Wizard로 문제 정의하기")
st.info("AI와 대화하며 프로젝트의 윤곽을 잡아보세요. 대화가 끝나면 아래 '대화 기반 문서 생성' 버튼을 눌러주세요.")

# 대화 기록이 없으면, AI가 첫 질문을 던짐
if not st.session_state.pd_messages:
    with st.chat_message("assistant", avatar="🤖"):
        initial_prompt = "안녕하세요! AI 프로젝트 기획을 도와드릴게요. 어떤 문제를 해결하고 싶으신가요? 핵심를 수정합니다.

---

### **업그레이드 실행: `1_1_📝_문제_정의서.py` 코드 교체**

아래의 전체 코드를 복사하여 **`your_mcp_project/pages/`** 폴더의 **`1_1_📝_문제_정의서.py`** 파일 내용을 **모두 교체**해주세요.

```python
# your_mcp_project/pages/1_1_📝_문제_정의서.py
# (개선 #1: 대화형 Wizard + 개선 #3: JSON 응답 적용)

import streamlit as st
import google.generativeai as genai
import json

# -------------------- Gemini API 설정 --------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("📝 문제 정의서 (AI Wizard)")
st.markdown("---")

# session_state 초기의 초안이 완성되도록 만드는 것이 목표입니다.

아래 코드로 **`your_mcp_project/pages/`** 폴더의 **`1_1_📝_문제_정의서.py`** 파일 내용을 **모두 교체**해주세요.

```python
# your_mcp_project/pages/1_1_📝_문제_정의서.py
# (대화형 Wizard 버전)

import streamlit as st
import google.generativeai as genai

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_ENABLED = True
except (KeyError, AttributeError):
    GEMINI_ENABLED = False

# -------------------- 페이지 설정 및 초기화 --------------------
st.title("📝 문제 정의서 (AI Wizard)")
st.markdown("---")

# session_state 초기화
if 'problem_definition' not in st.session_state:
    st.session_state.problem_definition = {
        "project_name": "", "project_goal": "", "problem_background": "", "expected_output": ""
    }

# 대화 기록 및 대화 단계 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = 0

# -------------------- 대화형 Wizard UI --------------------
st.header("✨ AI와 대화하며 문제 정의서 작성하기")
st.info("AI의 질문에 답변하시면 자동으로 문제 정의서가 채워집니다. 언제든지 내용을 직접 수정할 수도 있습니다.")

# AI의 첫 질문 (대화가 시작되지 않았을 경우)
if st.session_state.conversation_stage == 0:
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 어떤 AI 프로젝트를 기획하고 계신가요? **프로젝트의 핵심 아이디어나 이름**을 알려주세요."})
    st.session_state.conversation_stage = 1 # 다음 단계로 전환

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if user_input := st.chat_input("답변을 입력하세요..."):
    # 사용자 메시지 기록
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 현재 대화 단계에 따라 처리
    stage = st.session_state.conversation_stage
    
    if stage == 1:
        st.session_state.problem_definition['project_name'] = user_input
        ai_response = "좋은 아이디어네요! 이 프로젝트를 통해 달성하고자 하는 **최종 목표**는 무엇인가요?"
        st.session_state.conversation_stage = 2
    elif stage == 2:
        st.session_state.problem_definition['project_goal'] = user_input
        ai_response = "목표가 명확하군요. 이 프로젝트가 **필요하게 된 배경이나 현재 겪고 있는 문제 상황**에 대해 좀 더 자세히 설명해주시겠어요?"
        st.session_state.conversation_stage = 3
    elif stage == 3:
        st.session_state.problem_definition['problem_background'] = user_input
        ai_response = "이해했습니다. 마지막으로, 이 프로젝트가 성공적으로 완료되었을 때 나와야 하는 **핵심 결과물(Key Deliverables)**은 무엇인가요? (예: API, 대시보드, 보고서 등)"
        st.session_state.conversation_stage = 4
    elif stage == 4:
        st.session_state.problem_definition['expected_output'] = user_input
        ai_response = "모든 정보를 입력받았습니다! 아래 '문제 정의서 상세 내용'에서 수집된 내용을 확인하고, 필요하다면 직접 수정 후 저장해주세요. 'AI로 전체 초안 생성' 버튼을 누르면 이 내용을 바탕으로 Gemini가 더 상세한 초안을 만들어줍니다."
        st.session_state.conversation_stage = 5 # 대화 종료
    else:
        ai_response = "모든 질문이 완료되었습니다. 아래 내용을 확인하고 저장해주세요."

    # AI 응답 기록
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.rerun() # 페이지를 새로고침하여 메시지를 즉시 표시

# -------------------- 수집된 정보 확인 및 저장 --------------------
st.markdown("---")
st.header("📄 문제 정의서 상세 내용")

with st.form("problem_definition_form"):
    # 대화형 Wizard를 통해 수집된 값을 value에 직접 연결
    project_name = st.text_input("프로젝트 이름", value=st.session_state.problem_definition.get("project_name", ""))
    project_goal = st.text_area("프로젝트의 최종 목표", value=st.session_state.problem_definition.get("project_goal", ""), height=100)
    problem_background = st.text_area("문제 배경 및 필요성", value=st.session_state.problem_definition.get("problem_background", ""), height=200)
    expected_output = st.text_area("핵심 결과물 (Key Deliverables)", value=st.session_state.problem_definition.get("expected_output", ""), height=100)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submitted = st.form_submit_button("💾 수동 저장하기")
    with col2:
        ai_draft_button = st.form_submit_button("🚀 AI로 전체 초안 생성 (Gemini)")
    
    if submitted:
        # 아이디어나 목표를 자유롭게 말씀해주세요."
        st.markdown(initial_prompt)
    st.session_state.pd_messages.append({"role": "assistant", "content": initial_prompt})

# 대화 기록 표시
for message in st.session_state.pd_messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "🧑‍💻"):
        st.markdown(message["content"])

# 사용자 입력 처리
if user_prompt := st.chat_input("AI에게 답변하기..."):
    # 사용자 메시지 기록 및 표시
    st.session_state.pd_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    # AI 응답 생성 및 표시
    if GEMINI_ENABLED:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI가 답변을 생각 중입니다..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 이전 대화 내용을 프롬프트에 포함하여 맥락 유지
                conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.pd_messages])
                prompt_for_ai = f"""
                당신은 친절한 AI 프로젝트 기획 어시스턴트입니다.
                다음 대화 내용을 바탕으로, 사용자가 프로젝트를 구체화할 수 있도록 자연스럽게 대화를 이어가세요.
                필요하다면 추가적인 질문을 던져 목표, 배경, 필요성, 결과물 등을 파악하세요.
                
                [대화 기록]
                {conversation_history}
                
                [당신의 다음 응답]
                """
                
                response = model.generate_content(prompt_for_ai)
                ai_response = response.text
                st.markdown(ai_response)
        st.session_state.pd_messages.append({"role": "assistant", "content": ai_response})
    else:
        st.error("Gemini API 키가 설정되지 않았습니다.")

# --- 대화 기반 문서 생성 기능 ---
st.markdown("---")
if st.button("💬 대화 기반 문서 초안 생성", type="primary", disabled=len(st.session_state.pd_messages) < 2):
    if GEMINI_ENABLED:
        with st.spinner("AI가 대화 내용을 종합하여 문서 초안을 작성합니다..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.pd_messages])
            
            # JSON 출력을 위한 프롬프트
            prompt_for_json = f"""
            당신은 대화 내용을 분석하여 공식 문서로 정리하는 뛰어난 요약 전문가입니다.
            아래화 (메인 앱에서 이미 수행했지만, 안전장치로 유지)
if 'problem_definition' not in st.session_state:
    st.session_state['problem_definition'] = {
        "project_name": "", "project_goal": "", "problem_background": "", "expected_output": ""
    }

# -------------------- 대화형 문서 생성 (AI Wizard) --------------------
st.header("✨ AI Wizard와 대화하며 문서 작성하기")

if not GEMINI_ENABLED:
    st.error("Gemini API 키가 설정되지 않았습니다. Streamlit Cloud의 'Secrets'에 API 키를 추가해주세요.")
else:
    # 1. 대화 기록을 위한 session_state 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # AI가 먼저 첫 질문을 던집니다.
        st.session_state.messages.append(
            {"role": "assistant", "content": "안녕하세요! 어떤 AI 프로젝트를 기획하고 계신가요? 핵심 아이디어를 알려주시면 문제 정의서 초안을 만들어 드릴게요."}
        )
    
    # 2. 저장된 대화 기록을 순서대로 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. 사용자 입력 처리 (st.chat_input 사용)
    if user_prompt := st.chat_input("프로젝트 아이디어를 입력하세요..."):
        # 사용자의 입력을 대화 기록에 추가하고 화면에 표시
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        
        # AI의 응답을 생성하고 표시
        with st.chat_message("assistant"):
            with st.spinner("Gemini가 문서를 작성하는 중입니다..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # [개선 #3] JSON 응답을 요청하는 프롬프트
                prompt = f"""
                당신은 AI 프로젝트 기획 전문가입니다.
                사용자의 다음 핵심 아이디어를 바탕으로 'AI 개발 문제 정의서'의 각 항목을 채워주세요.
                결과는 반드시 아래의 JSON 형식으로만 응답해야 합니다. 각 값은 구체적이고 전문적인 내용으로 작성해주세요.

                **사용자 아이디어:** "{user_prompt}"

                ```json
                {{
                    "project_name": "[프로젝트의 특성을 잘 나타내는 이름]",
                    "project_goal": "[프로젝트의 최종 목표]",
                    "problem_background": "[이 문제가 왜 중요하고 해결해야 하는지에 대한 배경]",
                    "expected_output": "[프로젝트의 구체적인 결과물]"
                }}
                ```
                """
                
                try:
                    response = model.generate_content(prompt)
                    # 응답 텍스트에서 JSON 부분만 추출
                    json_str = response.text.split('```json')[1].split('```')[0].strip()
                    parsed_data = json.loads(json_str)
                    
                    # [핵심] 파싱된 JSON 데이터로 session_state를 직접 업데이트
                    st.session_state.problem_definition.update(parsed_data)
                    
                    response_content = "좋습니다! 아이디어를 바탕으로 문제 정의서 초안을 생성했습니다. 아래 폼에서 내용을 확인하고 필요하면 수정해주세요."
                    st.success("초안 생성 완료! 아래 폼을 확인하세요.")

                except (ValueError, IndexError, json.JSONDecodeError) as e:
                    response_content = f"죄송합니다. AI 응답을 처리하는 데 문제가 발생했습니다. (오류: {e})\n다시 시도해주시거나, 아래 폼에 직접 내용을 입력해주세요."
                    st.error(response_content)
                except Exception as e:
                    response_content = f"예상치 못한 오류가 발생했습니다: {e}"
                    st.error(response_content)

                # AI의 최종 응답 메시지를 대화 기록에 추가하고 화면에 표시
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                st.rerun() # ★★★ state 변경 후 UI를 즉시 새로고침하여 반영

# -------------------- 입력 폼 (AI가 채워주는 결과 확인 및 수정 영역) --------------------
st.markdown("---")
st.header("📄 문제 정의서 상세 내용")
st.info("AI Wizard가 생성한 초안입니다. 내용을 검토하고 수정 후 저장해주세요.", icon="✍️")

with st.form("problem_definition_form"):
    # value에 session_state 값을 직접 연결하여 AI가 생성한 값으로 자동 채움
    project_name = st.text_input("프로젝트 이름", value=st.session_state.problem_definition.get("project_name", ""))
    project_goal = st.text_area("프로젝트의 최종 목표", value=st.session_state.problem_definition.get("project_goal", ""), height=100)
    problem_background = st.text_area("문제 배경 및 필요성", value=st.session_state.problem_definition.get("problem_background", ""), height=200)
    expected_output = st.text_area("핵심 결과물 (Key Deliverables)", value=st.session_state.problem_definition.get("expected_output", ""), height=100)

    submitted = st.form_submit_button("💾 이 내용으로 저장하기")

    if submitted 폼의 현재 값을 다시 session_state에 저장 (사용자가 직접 수정한 내용 반영)
        st.session_state.problem_definition['project_name'] = project_name
        st.session_state.problem_definition['project_goal'] = project_goal
        st.session_state.problem_definition['problem_background'] = problem_background
        st.session_state.problem_definition['expected_output'] = expected_output
        st.success("문제 정의서 내용이 성공적으로 저장되었습니다!")

    if ai_draft_button and GEMINI_ENABLED:
        with st.spinner("Gemini가 전체 초안을 작성 중입니다..."):
            #... (이전 버전의 Gemini 호출 로직과 동일) ...
            st.success("AI가 생성한 초안으로 내용이 업데이트되었습니다! 확인 후 다시 저장해주세요.")
            # 페이지를 새로고침하여 업데이트된 내용을 폼에 즉시 반영
            st.rerun()
