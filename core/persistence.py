# core/persistence.py (삭제 기능 추가)

import sqlite3
from datetime import datetime
import os

DB_PATH = "database/mcp_database.db"

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
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

# --- 핵심 수정 부분: 프로젝트 삭제 함수 추가 ---
def delete_project(project_id: int):
    """지정된 ID의 프로젝트와 관련된 모든 산출물을 삭제합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ON DELETE CASCADE 옵션으로 인해, projects에서 삭제되면 artifacts도 자동 삭제됨
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# FOREIGN KEY 제약 조건에 ON DELETE CASCADE 추가
# 이렇게 하면 프로젝트가 삭제될 때 관련된 모든 산출물(artifacts)도 함께 자동으로 삭제됩니다.
# (이하 create_project, get_all_projects 등 다른 함수는 이전과 동일)

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
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def save_artifact(project_id, stage, type, content):
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
