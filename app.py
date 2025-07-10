# app.py - 메인 앱 파일 수정 사항

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import traceback
import sys
import os

# 디버깅 모드 활성화
DEBUG_MODE = True

def debug_info(message):
    """디버깅 정보 출력"""
    if DEBUG_MODE:
        st.sidebar.write(f"🔍 DEBUG: {message}")

def init_database():
    """데이터베이스 초기화"""
    try:
        conn = sqlite3.connect('projects.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # 테이블 생성 (존재하지 않으면)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        debug_info("데이터베이스 초기화 완료")
        return conn
        
    except Exception as e:
        st.error(f"데이터베이스 초기화 오류: {str(e)}")
        st.text(traceback.format_exc())
        return None

def init_session_state():
    """세션 상태 초기화"""
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = init_database()
    
    if 'projects' not in st.session_state:
        st.session_state.projects = []
    
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    
    debug_info(f"세션 상태 키: {list(st.session_state.keys())}")

def create_project(name, description):
    """프로젝트 생성"""
    try:
        conn = st.session_state.db_connection
        if not conn:
            st.error("데이터베이스 연결이 없습니다.")
            return False
        
        cursor = conn.cursor()
        
        # 프로젝트 삽입
        cursor.execute('''
            INSERT INTO projects (name, description, status, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, description, 'active', datetime.now()))
        
        # 반드시 커밋
        conn.commit()
        
        project_id = cursor.lastrowid
        debug_info(f"프로젝트 생성 완료: ID={project_id}")
        
        # 세션 상태 업데이트
        st.session_state.current_project = project_id
        
        return True
        
    except Exception as e:
        st.error(f"프로젝트 생성 오류: {str(e)}")
        st.text(traceback.format_exc())
        return False

def get_projects():
    """모든 프로젝트 조회"""
    try:
        conn = st.session_state.db_connection
        if not conn:
            debug_info("데이터베이스 연결이 없음")
            return pd.DataFrame()
        
        # 데이터 조회
        query = "SELECT id, name, description, status, created_at FROM projects ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn)
        
        debug_info(f"조회된 프로젝트 수: {len(df)}")
        
        # 빈 데이터프레임인 경우 샘플 데이터 생성
        if df.empty:
            debug_info("프로젝트 데이터가 없음")
            return pd.DataFrame({
                'ID': [],
                '이름': [],
                '설명': [],
                '상태': [],
                '생성일': []
            })
        
        # 컬럼명 한글로 변경
        df.columns = ['ID', '이름', '설명', '상태', '생성일']
        
        return df
        
    except Exception as e:
        st.error(f"프로젝트 조회 오류: {str(e)}")
        st.text(traceback.format_exc())
        return pd.DataFrame()

def validate_environment():
    """환경 설정 검증"""
    st.sidebar.header("환경 검증")
    
    checks = []
    
    # 1. Python 버전 확인
    python_version = sys.version
    checks.append(("Python 버전", python_version))
    
    # 2. 필수 패키지 확인
    required_packages = [
        'streamlit', 'sqlite3', 'pandas', 'datetime'
    ]
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
                checks.append((f"패키지 {package}", "✅ 설치됨"))
            elif package == 'streamlit':
                import streamlit
                checks.append((f"패키지 {package}", f"✅ v{streamlit.__version__}"))
            elif package == 'pandas':
                import pandas
                checks.append((f"패키지 {package}", f"✅ v{pandas.__version__}"))
            else:
                __import__(package)
                checks.append((f"패키지 {package}", "✅ 설치됨"))
        except ImportError:
            checks.append((f"패키지 {package}", "❌ 누락"))
    
    # 3. 데이터베이스 연결 확인
    try:
        conn = st.session_state.get('db_connection')
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            checks.append(("DB 연결", f"✅ 테이블 {len(tables)}개"))
        else:
            checks.append(("DB 연결", "❌ 연결 없음"))
    except Exception as e:
        checks.append(("DB 연결", f"❌ 오류: {str(e)}"))
    
    # 4. Gemini API 키 확인
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            checks.append(("Gemini API Key", f"✅ 설정됨 (길이: {len(api_key)})"))
        else:
            checks.append(("Gemini API Key", "❌ 미설정"))
    except Exception as e:
        checks.append(("Gemini API Key", f"❌ 오류: {str(e)}"))
    
    # 검증 결과 표시
    for check_name, result in checks:
        st.sidebar.text(f"{check_name}: {result}")

def main():
    """메인 함수"""
    st.set_page_config(
        page_title="MCP 기반 AI 개발 플랫폼",
        page_icon="🚀",
        layout="wide"
    )
    
    # 세션 상태 초기화
    init_session_state()
    
    # 환경 검증 (디버깅 모드일 때만)
    if DEBUG_MODE:
        validate_environment()
    
    # 메인 화면
    st.title("🚀 MCP 기반 AI 개발 플랫폼")
    
    # 프로젝트 목록 섹션
    st.header("프로젝트 목록")
    
    # 프로젝트 데이터 조회
    projects_df = get_projects()
    
    if not projects_df.empty:
        st.dataframe(projects_df, use_container_width=True)
    else:
        st.info("생성된 프로젝트가 없습니다.")
    
    # 새 프로젝트 생성 섹션
    st.header("새 프로젝트 생성")
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("프로젝트 이름", placeholder="프로젝트 이름을 입력하세요")
        
        with col2:
            project_description = st.text_area("프로젝트 설명", placeholder="프로젝트 설명을 입력하세요")
        
        submitted = st.form_submit_button("프로젝트 생성")
        
        if submitted:
            if project_name and project_description:
                if create_project(project_name, project_description):
                    st.success("프로젝트가 성공적으로 생성되었습니다!")
                    st.experimental_rerun()
                else:
                    st.error("프로젝트 생성에 실패했습니다.")
            else:
                st.error("프로젝트 이름과 설명을 모두 입력해주세요.")
    
    # 데이터베이스 상태 표시 (디버깅 모드)
    if DEBUG_MODE:
        st.header("데이터베이스 상태")
        try:
            conn = st.session_state.db_connection
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM projects")
                count = cursor.fetchone()[0]
                st.write(f"총 프로젝트 수: {count}")
                
                # 최근 프로젝트 5개 표시
                cursor.execute("SELECT * FROM projects ORDER BY created_at DESC LIMIT 5")
                recent = cursor.fetchall()
                if recent:
                    st.write("최근 프로젝트:")
                    for project in recent:
                        st.write(f"ID: {project[0]}, 이름: {project[1]}, 설명: {project[2]}")
        except Exception as e:
            st.error(f"데이터베이스 상태 확인 오류: {str(e)}")

if __name__ == "__main__":
    main()
