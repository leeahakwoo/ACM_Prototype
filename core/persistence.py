# core/persistence.py (수정 기능 추가)

import sqlite3
from datetime import datetime
import os

DB_PATH = "database/mcp, 사용자 실수를 방지하고 UI를 깔끔하게 유지합니다.
*   **수정 기능:** '수정' 버튼을 누르면, 선택된 프로젝트의 현재 이름과 설명이 사이드바의 입력창에 나타_database.db"

# (init_db, create_project, get_all_projects, delete_project 함수는 이전과 동일하게 유지)
def init_db():
    db_dir = os.path.dirname나 사용자가 수정하고 저장할 수 있도록 합니다.

---

### **수정된 코드 (전체 교체)**

아래 두 파일(`app.py`, `core/persistence.py`)의 내용을 **전부 교체(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.**해주세요. 이번 버전은 UI/UX와 데이터 처리 방식을 완전히 바꾸어 문제를 근본적으로 해결합니다.

#### **1. `core/persistence.py` 최종 수정**

`update_project` 함수를 추가하고, `ONcursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL
    )
 DELETE CASCADE` 옵션을 확실히 적용합니다.

```python
# core/persistence.py (수정/삭제 기능    """)
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
    conn. 최종 버전)

import sqlite3
from datetime import datetime
import os

DB_PATH = "database/mcp_database.db"

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()close()

def create_project(name, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)", 
                   (name, description, now))
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3
    
    # 데이터베이스 연결 시 외부 키 제약 조건 활성화
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
        stage TEXT NOT.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def delete_project(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON") # CASCADE 옵션 활성화
    cursor.execute("DELETE FROM projects WHERE id = ?", NULL,
        type TEXT NOT NULL,
        content TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close (project_id,))
    conn.commit()
    conn.close()

# --- 핵심 추가 부분: 프로젝트 수정 함수 ---
def update_project(project_id: int, new_name: str, new_description: str):
    """지정된 ID의 프로젝트 이름과 설명을 수정합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET name = ?, description = ? WHERE id = ?", 
                   (new_name, new_description, project_id))
    conn.commit()
    conn.close()

# (save_artifact, get_artifacts_for_project 함수는 이전과 동일)
def save_artifact(project_id, stage, type, content):
    conn = sqlite3.()
    return projects

def create_project(name, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)",
                       (name, description, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # 이름 중복 방지
        return False
    finally:
        conn.close()

def update_project(project_id, name, description):
    """프로젝트 이름과 설명을 수정합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATEconnect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("INSERT INTO artifacts (project_id, stage, type, content, created_at) VALUES (?, ?, ?, ?, ?)", (project_id, stage, type, content, now))
    conn.commit()
    conn.close()

def get_artifacts_for_project(project_id, type):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT content, created_at FROM artifacts WHERE project_id = ? AND type = ? ORDER BY created_at DESC", (project_id, type))
    artifacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return artifacts
