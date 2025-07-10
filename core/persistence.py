# core/persistence.py
# (폴더 자동 생성 기능이 추가된 버전)

import sqlite3
import json
from datetime import datetime
import os # os 모듈 임포트

DB_PATH = "database/mcp_database.db"

def init_db():
    """DB 파일과 테이블을 초기화합니다. DB가 위치할 폴더도 자동으로 생성합니다."""
    
    # --- 핵심 수정 부분 ---
    # DB 파일이 위치할 디렉토리 경로 추출
    db_dir = os.path.dirname(DB_PATH)
    # 해당 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    # --- 수정 끝 ---

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 프로젝트 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL
    )
    """)
    # 산출물 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        stage TEXT NOT NULL,
        type TEXT NOT NULL,
        content TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    """)
    conn.commit()
    conn.close()

def create_project(name, description):
    """새 프로젝트를 생성합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)", 
                   (name, description, now))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def get_all_projects():
    """모든 프로젝트 목록을 불러옵니다."""
    conn = sqlite3.connect(DB_PATH)
    # 튜플 대신 딕셔너리 형태로 결과를 받기 위해 row_factory 설정
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    projects = [dict(row) for row in cursor.fetchall()] # 딕셔너리 리스트로 변환
    conn.close()
    return projects

def save_artifact(project_id, stage, type, content):
    """생성된 산출물을 DB에 저장합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO artifacts (project_id, stage, type, content, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (project_id, stage, type, content, now))
    conn.commit()
    conn.close()

def get_artifacts_for_project(project_id, type):
    """특정 프로젝트의 특정 타입 산출물을 모두 불러옵니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    SELECT content, created_at FROM artifacts
    WHERE project_id = ? AND type = ?
    ORDER BY created_at DESC
    """, (project_id, type))
    artifacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return artifacts
