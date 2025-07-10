# persistence.py (캐시 제거, 직접 연결 방식으로 복귀)

import sqlite3
from datetime import datetime
import os
import streamlit as st

DB_PATH = "database/mcp_database.db"

def init_db():
    """DB 파일과 테이블을 초기화합니다."""
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # 연결을 생성하고 바로 닫아 파일 및 테이블 구조만 확인
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
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
    conn.close()


def execute_query(query, params=(), commit=False, fetch_one=False):
    """
    DB 쿼리 실행을 위한 중앙 함수.
    매번 새로운 연결을 생성하여 상태 충돌을 방지합니다.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        else:
            if fetch_one:
                result = cursor.fetchone()
                data = dict(result) if result else None
            else:
                results = cursor.fetchall()
                data = [dict(row) for row in results]
            conn.close()
            return data
            
    except sqlite3.Error as e:
        st.error(f"데이터베이스 오류: {e}")
        return None if commit or fetch_one else []


def get_all_projects():
    return execute_query("SELECT * FROM projects ORDER BY created_at DESC")

def create_project(name, description):
    query = "INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)"
    params = (name, description, datetime.now().isoformat())
    return execute_query(query, params, commit=True)

def update_project(project_id, name, description):
    query = "UPDATE projects SET name = ?, description = ? WHERE id = ?"
    params = (name, description, project_id)
    execute_query(query, params, commit=True)

def delete_project(project_id):
    query = "DELETE FROM projects WHERE id = ?"
    params = (project_id,)
    execute_query(query, params, commit=True)

def save_artifact(project_id, stage, type, content):
    query = "INSERT INTO artifacts (project_id, stage, type, content, created_at) VALUES (?, ?, ?, ?, ?)"
    params = (project_id, stage, type, content, datetime.now().isoformat())
    execute_query(query, params, commit=True)

def get_artifacts_for_project(project_id, type):
    query = "SELECT * FROM artifacts WHERE project_id = ? AND type = ? ORDER BY created_at DESC"
    params = (project_id, type)
    return execute_query(query, params)
