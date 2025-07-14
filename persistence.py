# persistence.py (사용자 설정 저장 기능 추가)

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = "app_data.db"

def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 기존 프로젝트 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 사용자 설정 테이블 (새로 추가)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # 프로젝트 상태 테이블 (새로 추가)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            state_key TEXT NOT NULL,
            state_value TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_projects():
    """모든 프로젝트 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = cursor.fetchall()
    conn.close()
    
    return [{"id": p[0], "name": p[1], "description": p[2], "created_at": p[3]} for p in projects]

def get_project_by_id(project_id):
    """특정 프로젝트 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    
    if project:
        return {"id": project[0], "name": project[1], "description": project[2], "created_at": project[3]}
    return None

def create_project(name, description):
    """새 프로젝트 생성"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)',
            (name, description, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def update_project(project_id, name, description):
    """프로젝트 수정"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE projects SET name = ?, description = ? WHERE id = ?',
        (name, description, project_id)
    )
    conn.commit()
    conn.close()

def delete_project(project_id):
    """프로젝트 삭제"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

# --- 사용자 설정 관련 함수들 (새로 추가) ---

def save_user_settings(settings_dict):
    """사용자 설정 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 설정을 JSON 문자열로 변환하여 저장
    settings_json = json.dumps(settings_dict)
    current_time = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_settings (setting_key, setting_value, updated_at)
        VALUES (?, ?, ?)
    ''', ('main_settings', settings_json, current_time))
    
    conn.commit()
    conn.close()

def get_user_settings():
    """사용자 설정 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT setting_value FROM user_settings WHERE setting_key = ?', ('main_settings',))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        try:
            return json.loads(result[0])
        except json.JSONDecodeError:
            return {}
    return {}

def save_project_state(project_id, state_key, state_value):
    """프로젝트별 상태 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 상태를 JSON 문자열로 변환
    state_json = json.dumps(state_value) if not isinstance(state_value, str) else state_value
    current_time = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT OR REPLACE INTO project_states (project_id, state_key, state_value, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (project_id, state_key, state_json, current_time))
    
    conn.commit()
    conn.close()

def get_project_state(project_id, state_key):
    """프로젝트별 상태 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT state_value FROM project_states 
        WHERE project_id = ? AND state_key = ?
    ''', (project_id, state_key))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        try:
            return json.loads(result[0])
        except json.JSONDecodeError:
            return result[0]
    return None

def get_all_project_states(project_id):
    """특정 프로젝트의 모든 상태 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT state_key, state_value FROM project_states 
        WHERE project_id = ?
    ''', (project_id,))
    results = cursor.fetchall()
    conn.close()
    
    states = {}
    for state_key, state_value in results:
        try:
            states[state_key] = json.loads(state_value)
        except json.JSONDecodeError:
            states[state_key] = state_value
    
    return states

def backup_all_data():
    """모든 데이터 백업"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 모든 테이블 데이터 추출
    backup_data = {}
    
    # 프로젝트 데이터
    cursor.execute('SELECT * FROM projects')
    backup_data['projects'] = cursor.fetchall()
    
    # 사용자 설정 데이터
    cursor.execute('SELECT * FROM user_settings')
    backup_data['user_settings'] = cursor.fetchall()
    
    # 프로젝트 상태 데이터
    cursor.execute('SELECT * FROM project_states')
    backup_data['project_states'] = cursor.fetchall()
    
    conn.close()
    
    # 백업 파일 생성
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    return backup_filename

def restore_from_backup(backup_file):
    """백업 파일로부터 데이터 복원"""
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM project_states')
        cursor.execute('DELETE FROM user_settings')
        cursor.execute('DELETE FROM projects')
        
        # 프로젝트 데이터 복원
        for project in backup_data.get('projects', []):
            cursor.execute('''
                INSERT INTO projects (id, name, description, created_at)
                VALUES (?, ?, ?, ?)
            ''', project)
        
        # 사용자 설정 데이터 복원
        for setting in backup_data.get('user_settings', []):
            cursor.execute('''
                INSERT INTO user_settings (id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, ?)
            ''', setting)
        
        # 프로젝트 상태 데이터 복원
        for state in backup_data.get('project_states', []):
            cursor.execute('''
                INSERT INTO project_states (id, project_id, state_key, state_value, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', state)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"백업 복원 중 오류 발생: {e}")
        return False

def clear_expired_sessions():
    """만료된 세션 데이터 정리 (선택사항)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 7일 이상 된 프로젝트 상태 데이터 삭제
    week_ago = datetime.now() - timedelta(days=7)
    cursor.execute('''
        DELETE FROM project_states 
        WHERE updated_at < ?
    ''', (week_ago.isoformat(),))
    
    conn.commit()
    conn.close()
