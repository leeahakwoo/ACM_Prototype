# persistence.py (모든 함수가 포함된 최종 완전판)

import sqlite3
from datetime import datetime
import os

DB_PATH = "database/mcp_database.db"

def init_db():
    """DB 파일과 테이블을 초기화합니다. DB가 위치할 폴더도 자동으로 생성합니다."""
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 데이터베이스 연결 시 외부 키 제약 조건 활성화
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 프로젝트 테이블 (이름은 중복될 수 없도록 UNIQUE 제약 조건 추가)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TEXT NOT NULL
    )
    """)
    # 산출물 테이블 (프로젝트 삭제 시 함께 삭제되도록 ON DELETE CASCADE 추가)
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

def get_all_projects():
    """모든 프로젝트 목록을 불러옵니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def create_project(name, description):
    """새 프로젝트를 생성합니다. 이름이 중복되면 False를 반환합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)",
                       (name, description, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # 이름 중복 시 발생하는 오류
        return False
    finally:
        conn.close()

def update_project(project_id, name, description):
    """프로젝트 이름과 설명을 수정합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET name = ?, description = ? WHERE id = ?",
                   (name, description, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    """프로젝트와 관련된 모든 산출물을 삭제합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    
# --- 이 아래 두 함수가 누락되었을 가능성이 높습니다. ---

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
