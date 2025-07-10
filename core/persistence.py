# core/persistence.py
import sqlite3
import json
from datetime import datetime

DB_PATH = "database/mcp_database.db"

def init_db():
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
        stage TEXT NOT NULL, -- 예: 'REQUIREMENT'
        type TEXT NOT NULL,  -- 예: 'PROBLEM_DEF'
        content TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    """)
    conn.commit()
    conn.close()

def create_project(name, description):
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    projects = cursor.fetchall()
    conn.close()
    return projects

# (save_artifact, get_artifacts 등 함수 추가 예정)
