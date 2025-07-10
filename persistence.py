# persistence.py (상태 관리 및 트랜잭션 강화 버전)

import sqlite3
from datetime import datetime
import os
import streamlit as st

DB_PATH = "database/mcp_database.db"

@st.cache_resource
def get_db_connection():
    """
    Streamlit의 캐시를 사용하여 DB 연결을 한 번만 생성하고 재사용합니다.
    """
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # 외부 키 제약 조건 활성화
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """DB 테이블을 초기화합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        stage TEXT NOT NULL,
        type TEXT NOT NULL,
        content TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
    )
    """)
    conn.commit()

# (이하 모든 함수는 get_db_connection()을 사용하도록 변경)

def execute_query(query, params=(), commit=False):
    """DB 쿼리 실행을 위한 래퍼 함수 (에러 핸들링 포함)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
            return cursor.lastrowid
        else:
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        st.error(f"데이터베이스 오류: {e}")
        return None if commit else []
    
def get_all_projects():
    return execute_query("SELECT * FROM projects ORDER BY created_at DESC")

def create_project(name, description):
    query = "INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)"
    params = (name, description, datetime.now().isoformat())
    return execute_query(query, params, commit=True)

def update_project(project_id, name, description):
    query = "UPDATE projects SET name = ?, description = ? WHERE id = ?"
    params = (name, description, project_id)
    return execute_query(query, params, commit=True)

def delete_project(project_id):
    query = "DELETE FROM projects WHERE id = ?"
    params = (project_id,)
    return execute_query(query, params, commit=True)

def save_artifact(project_id, stage, type, content):
    query = "INSERT INTO artifacts (project_id, stage, type, content, created_at) VALUES (?, ?, ?, ?, ?)"
    params = (project_id, stage, type, content, datetime.now().isoformat())
    return execute_query(query, params, commit=True)

def get_artifacts_for_project(project_id, type):
    query = "SELECT * FROM artifacts WHERE project_id = ? AND type = ? ORDER BY created_at DESC"
    params = (project_id, type)
    return execute_query(query, params)
