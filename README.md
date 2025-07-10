# 🚀 MCP 기반 AI 개발 플랫폼 (프로토타입)

이 프로젝트는 AI 모델 개발의 전체 생명주기(요구사항 정의, 설계, 검증 등)에 필요한 문서와 산출물을 체계적으로 관리하고, AI를 통해 생성을 자동화하는 플랫폼의 프로토타입입니다.

## ✨ 주요 기능

- **프로젝트 관리:** 여러 AI 프로젝트를 생성, 수정, 삭제하고 관리할 수 있는 대시보드.
- **문서 자동화 (요구정의):** 사용자가 프로젝트의 핵심 정보를 입력하면, Gemini AI가 전문가 수준의 '문제정의서' 초안을 자동으로 작성.
- **영속적 데이터 저장:** 생성된 모든 프로젝트와 문서는 SQLite 데이터베이스에 안전하게 저장됩니다.
- **확장 가능한 아키텍처:** 향후 '설계', '검증' 등 새로운 개발 단계의 모듈을 쉽게 추가할 수 있는 구조.

## 🛠️ 기술 스택

- **프레임워크:** Streamlit
- **언어:** Python
- **LLM:** Google Gemini
- **데이터베이스:** SQLite

## 💻 로컬에서 실행하기

1.  **리포지토리 클론:**
    ```bash
    git clone https://github.com/leeahakwoo/ACM_Prototype.git
    cd ACM_Prototype
    ```

2.  **가상 환경 생성 및 활성화 (권장):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **필요한 패키지 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Streamlit Secrets 설정:**
    - 프로젝트 루트에 `.streamlit` 폴더를 생성합니다.
    - 그 안에 `secrets.toml` 파일을 만들고 아래 내용을 추가합니다.
    ```toml
    # .streamlit/secrets.toml
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
    ```

5.  **Streamlit 앱 실행:**
    ```bash
    streamlit run app.py
    ```

## ☁️ 배포

이 애플리케이션은 Streamlit Cloud를 통해 배포됩니다. 배포 시에는 Streamlit Cloud의 `Secrets` 설정 메뉴에 `GEMINI_API_KEY`를 직접 등록해야 합니다.
