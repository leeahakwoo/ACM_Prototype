# pages/1_요구정의.py - 요구사항 페이지 수정

import streamlit as st
import sqlite3
import traceback
import sys
import os

# 안전한 import 구문
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    st.error(f"Google Generative AI 패키지를 찾을 수 없습니다: {str(e)}")
    st.info("다음 명령어로 설치하세요: pip install google-generativeai")
    GEMINI_AVAILABLE = False
except Exception as e:
    st.error(f"Gemini AI 모듈 로드 중 오류: {str(e)}")
    GEMINI_AVAILABLE = False

def safe_import_check():
    """필수 패키지 import 확인"""
    missing_packages = []
    
    # 기본 패키지 확인
    try:
        import pandas
    except ImportError:
        missing_packages.append("pandas")
    
    try:
        import datetime
    except ImportError:
        missing_packages.append("datetime")
    
    if missing_packages:
        st.error(f"누락된 패키지: {', '.join(missing_packages)}")
        st.info("requirements.txt를 확인하고 필요한 패키지를 설치하세요.")
        return False
    
    return True

def init_gemini_api():
    """Gemini API 초기화"""
    try:
        if not GEMINI_AVAILABLE:
            return None
        
        # API 키 가져오기
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.error("Gemini API 키가 설정되지 않았습니다.")
            st.info("Streamlit Cloud의 Settings > Secrets에서 GEMINI_API_KEY를 설정하세요.")
            return None
        
        # API 설정
        genai.configure(api_key=api_key)
        
        # 모델 초기화
        model = genai.GenerativeModel('gemini-pro')
        
        return model
        
    except Exception as e:
        st.error(f"Gemini API 초기화 오류: {str(e)}")
        st.text(traceback.format_exc())
        return None

def get_project_info(project_id):
    """프로젝트 정보 조회"""
    try:
        # 세션에서 데이터베이스 연결 가져오기
        conn = st.session_state.get('db_connection')
        if not conn:
            st.error("데이터베이스 연결이 없습니다.")
            return None
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()
        
        if project:
            return {
                'id': project[0],
                'name': project[1],
                'description': project[2],
                'status': project[3],
                'created_at': project[4]
            }
        else:
            st.warning(f"프로젝트 ID {project_id}를 찾을 수 없습니다.")
            return None
            
    except Exception as e:
        st.error(f"프로젝트 정보 조회 오류: {str(e)}")
        st.text(traceback.format_exc())
        return None

def generate_requirements_document(project_info):
    """요구사항 문서 생성"""
    try:
        # Gemini 모델 초기화
        model = init_gemini_api()
        if not model:
            return None
        
        # 프롬프트 생성
        prompt = f"""
        다음 프로젝트 정보를 바탕으로 전문적인 요구사항 정의서를 작성해주세요.

        프로젝트명: {project_info['name']}
        프로젝트 설명: {project_info['description']}
        프로젝트 상태: {project_info['status']}

        요구사항 정의서는 다음 구조로 작성해주세요:
        1. 프로젝트 개요
        2. 기능 요구사항
        3. 비기능 요구사항
        4. 제약 조건
        5. 인수 조건

        전문적이고 구체적으로 작성해주세요.
        """
        
        # AI 응답 생성
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            st.error("AI 응답을 생성할 수 없습니다.")
            return None
            
    except Exception as e:
        st.error(f"요구사항 문서 생성 오류: {str(e)}")
        st.text(traceback.format_exc())
        return None

def save_requirements_document(project_id, content):
    """요구사항 문서 저장"""
    try:
        conn = st.session_state.get('db_connection')
        if not conn:
            st.error("데이터베이스 연결이 없습니다.")
            return False
        
        cursor = conn.cursor()
        
        # 요구사항 테이블 생성 (존재하지 않으면)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # 기존 요구사항 삭제 (업데이트 방식)
        cursor.execute("DELETE FROM requirements WHERE project_id = ?", (project_id,))
        
        # 새 요구사항 삽입
        cursor.execute('''
            INSERT INTO requirements (project_id, content)
            VALUES (?, ?)
        ''', (project_id, content))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"요구사항 문서 저장 오류: {str(e)}")
        st.text(traceback.format_exc())
        return False

def main():
    """메인 함수"""
    st.set_page_config(
        page_title="요구사항 정의",
        page_icon="📋",
        layout="wide"
    )
    
    # 패키지 import 확인
    if not safe_import_check():
        st.stop()
    
    st.title("📋 요구사항 정의")
    
    # 프로젝트 선택
    try:
        conn = st.session_state.get('db_connection')
        if not conn:
            st.error("데이터베이스 연결이 없습니다. 메인 페이지로 돌아가세요.")
            st.stop()
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM projects WHERE status = 'active'")
        projects = cursor.fetchall()
        
        if not projects:
            st.warning("활성 프로젝트가 없습니다. 먼저 프로젝트를 생성하세요.")
            st.stop()
        
        # 프로젝트 선택 박스
        project_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in projects}
        selected_project = st.selectbox(
            "프로젝트 선택",
            options=list(project_options.keys()),
            key="selected_project"
        )
        
        if selected_project:
            project_id = project_options[selected_project]
            
            # 프로젝트 정보 표시
            project_info = get_project_info(project_id)
            if project_info:
                st.subheader("프로젝트 정보")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**프로젝트명:** {project_info['name']}")
                    st.write(f"**상태:** {project_info['status']}")
                
                with col2:
                    st.write(f"**생성일:** {project_info['created_at']}")
                
                st.write(f"**설명:** {project_info['description']}")
                
                # 요구사항 문서 생성 버튼
                if st.button("요구사항 문서 생성", type="primary"):
                    with st.spinner("AI가 요구사항 문서를 생성하고 있습니다..."):
                        requirements_content = generate_requirements_document(project_info)
                        
                        if requirements_content:
                            # 문서 저장
                            if save_requirements_document(project_id, requirements_content):
                                st.success("요구사항 문서가 성공적으로 생성되고 저장되었습니다!")
                                
                                # 생성된 문서 표시
                                st.subheader("생성된 요구사항 문서")
                                st.markdown(requirements_content)
                                
                                # 다운로드 버튼
                                st.download_button(
                                    label="문서 다운로드",
                                    data=requirements_content,
                                    file_name=f"requirements_{project_info['name']}.txt",
                                    mime="text/plain"
                                )
                            else:
                                st.error("요구사항 문서 저장에 실패했습니다.")
                        else:
                            st.error("요구사항 문서 생성에 실패했습니다.")
                
                # 기존 요구사항 문서 확인
                try:
                    cursor.execute("SELECT content, created_at FROM requirements WHERE project_id = ? ORDER BY created_at DESC LIMIT 1", (project_id,))
                    existing_req = cursor.fetchone()
                    
                    if existing_req:
                        st.subheader("기존 요구사항 문서")
                        st.info(f"마지막 생성일: {existing_req[1]}")
                        
                        with st.expander("기존 문서 보기"):
                            st.markdown(existing_req[0])
                            
                            # 기존 문서 다운로드
                            st.download_button(
                                label="기존 문서 다운로드",
                                data=existing_req[0],
                                file_name=f"existing_requirements_{project_info['name']}.txt",
                                mime="text/plain"
                            )
                
                except Exception as e:
                    st.error(f"기존 요구사항 문서 조회 오류: {str(e)}")
            
    except Exception as e:
        st.error(f"페이지 로드 오류: {str(e)}")
        st.text(traceback.format_exc())
        st.info("메인 페이지로 돌아가서 다시 시도하세요.")

if __name__ == "__main__":
    main()
