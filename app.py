# app.py (세션 만료 대응 개선 버전)

import streamlit as st
from datetime import datetime
import sys
import os
import json

# --- 경로 설정 및 모듈 import ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from persistence import (
    init_db, get_all_projects, create_project, delete_project, update_project,
    # 추가로 필요한 함수들 (persistence.py에 구현 필요)
    save_user_settings, get_user_settings, get_project_by_id
)

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="대시보드 - AI 관리 지원 도구", 
    page_icon="🚀", 
    layout="wide"
)

# --- 앱 초기화 ---
init_db()

# --- 사용자 설정 복원 함수 ---
def restore_user_settings():
    """사용자 설정을 데이터베이스에서 복원"""
    try:
        settings = get_user_settings()
        if settings:
            # 마지막 선택된 프로젝트 복원
            if 'selected_project_id' in settings and settings['selected_project_id']:
                project = get_project_by_id(settings['selected_project_id'])
                if project:
                    st.session_state.selected_project_id = settings['selected_project_id']
                    st.session_state.selected_project_name = project['name']
                    st.success(f"이전 작업 프로젝트 '{project['name']}'가 복원되었습니다.")
            
            # 기타 설정들 복원
            if 'last_view_mode' in settings:
                st.session_state.view_mode = settings['last_view_mode']
    except Exception as e:
        st.warning(f"사용자 설정 복원 중 오류가 발생했습니다: {str(e)}")

# --- 사용자 설정 저장 함수 ---
def save_current_settings():
    """현재 세션 상태를 데이터베이스에 저장"""
    try:
        settings = {
            'selected_project_id': st.session_state.get('selected_project_id'),
            'selected_project_name': st.session_state.get('selected_project_name'),
            'last_view_mode': st.session_state.get('view_mode', 'table'),
            'last_updated': datetime.now().isoformat()
        }
        save_user_settings(settings)
    except Exception as e:
        st.error(f"설정 저장 중 오류가 발생했습니다: {str(e)}")

# --- session_state 관리 및 복원 ---
if 'editing_project' not in st.session_state:
    st.session_state.editing_project = None
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None
if 'selected_project_name' not in st.session_state:
    st.session_state.selected_project_name = None
if 'show_create_dialog' not in st.session_state:
    st.session_state.show_create_dialog = False
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'table'
if 'settings_restored' not in st.session_state:
    st.session_state.settings_restored = False
    restore_user_settings()
    st.session_state.settings_restored = True

# --- 자동 저장 함수 ---
def auto_save_settings():
    """중요한 상태 변경 시 자동으로 설정 저장"""
    if st.session_state.settings_restored:
        save_current_settings()

# --- 다이얼로그 함수 정의 ---
@st.dialog("새 프로젝트 생성")
def create_project_dialog():
    with st.form("new_project_dialog_form"):
        name = st.text_input("프로젝트 이름")
        desc = st.text_area("프로젝트 설명")
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("생성하기"):
            if name:
                if create_project(name, desc):
                    st.toast("프로젝트가 생성되었습니다.")
                    st.session_state.show_create_dialog = False
                    auto_save_settings()
                    st.rerun()
                else:
                    st.error("이미 존재하는 프로젝트 이름입니다.")
            else:
                st.error("프로젝트 이름을 입력해주세요.")
        
        if col_btn2.form_submit_button("취소", type="secondary"):
            st.session_state.show_create_dialog = False
            st.rerun()

# --- UI 그리기 ---
st.title("🚀 AI 관리 지원 도구")
st.header("대시보드")

# --- 상단 정보 바 ---
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("총 프로젝트 수", len(get_all_projects()))
with col_info2:
    if st.session_state.selected_project_id:
        st.metric("선택된 프로젝트", st.session_state.selected_project_name)
    else:
        st.metric("선택된 프로젝트", "없음")
with col_info3:
    # 데이터 백업 버튼
    if st.button("💾 현재 상태 저장", help="현재 선택된 프로젝트와 설정을 저장합니다"):
        save_current_settings()
        st.toast("설정이 저장되었습니다.")

st.markdown("---")

# --- 사이드바 ---
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 뷰 모드 선택
    view_mode = st.selectbox(
        "표시 방식",
        ["table", "card"],
        index=0 if st.session_state.view_mode == "table" else 1,
        format_func=lambda x: "테이블 뷰" if x == "table" else "카드 뷰"
    )
    if view_mode != st.session_state.view_mode:
        st.session_state.view_mode = view_mode
        auto_save_settings()
    
    st.divider()
    
    # 수정 모드일 때
    if st.session_state.editing_project:
        st.header("📝 프로젝트 수정")
        proj = st.session_state.editing_project
        with st.form("edit_form"):
            name = st.text_input("프로젝트 이름", value=proj['name'])
            desc = st.text_area("프로젝트 설명", value=proj['description'])
            if st.form_submit_button("수정 완료", type="primary"):
                update_project(proj['id'], name, desc)
                st.toast("프로젝트가 수정되었습니다.")
                st.session_state.editing_project = None
                # 선택된 프로젝트 이름 업데이트
                if st.session_state.selected_project_id == proj['id']:
                    st.session_state.selected_project_name = name
                auto_save_settings()
                st.rerun()
            if st.form_submit_button("취소"):
                st.session_state.editing_project = None
                st.rerun()
    # 생성 모드가 아닐 때의 안내 메시지
    else:
        st.info("프로젝트를 수정하려면 목록에서 '수정' 버튼을 클릭하세요.")
    
    st.divider()
    
    # 데이터 관리 섹션
    st.header("🔄 데이터 관리")
    if st.button("🔄 설정 복원", help="저장된 설정을 다시 불러옵니다"):
        restore_user_settings()
        st.toast("설정이 복원되었습니다.")
        st.rerun()

# --- 메인 콘텐츠: 프로젝트 목록 및 관리 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("프로젝트 목록")
with col2:
    if st.button("✚ 새 프로젝트 생성", type="primary", use_container_width=True):
        st.session_state.show_create_dialog = True

# --- 새 프로젝트 생성 다이얼로그 호출 ---
if st.session_state.show_create_dialog:
    create_project_dialog()

# --- 선택된 프로젝트 정보 표시 ---
if st.session_state.selected_project_id:
    st.success(f"현재 작업 중인 프로젝트: **{st.session_state.selected_project_name}** (ID: {st.session_state.selected_project_id})")
else:
    st.info("작업할 프로젝트를 아래 목록에서 '선택' 버튼을 눌러 지정해주세요.")
st.divider()

# --- 프로젝트 목록 표시 ---
projects = get_all_projects()
if not projects:
    st.info("생성된 프로젝트가 없습니다. '새 프로젝트 생성' 버튼을 클릭하여 시작하세요.")
else:
    if st.session_state.view_mode == "table":
        # 테이블 뷰
        header_cols = st.columns([1, 3, 4, 2, 3])
        header_cols[0].write("**ID**")
        header_cols[1].write("**이름**")
        header_cols[2].write("**설명**")
        header_cols[3].write("**생성일**")
        header_cols[4].write("**관리**")
        
        for proj in projects:
            row_cols = st.columns([1, 3, 4, 2, 3])
            row_cols[0].write(proj['id'])
            row_cols[1].write(proj['name'])
            row_cols[2].write(proj['description'])
            try:
                dt_object = datetime.fromisoformat(proj['created_at'])
                row_cols[3].write(dt_object.strftime('%Y-%m-%d %H:%M'))
            except (ValueError, TypeError):
                row_cols[3].write(proj['created_at'])
            
            with row_cols[4]:
                manage_cols = st.columns(3)
                is_selected = (st.session_state.selected_project_id == proj['id'])
                
                if manage_cols[0].button("✓" if is_selected else "선택", key=f"select_{proj['id']}", type="primary" if is_selected else "secondary", help="이 프로젝트를 작업 대상으로 선택합니다."):
                    st.session_state.selected_project_id = proj['id']
                    st.session_state.selected_project_name = proj['name']
                    auto_save_settings()
                    st.rerun()

                if manage_cols[1].button("수정", key=f"edit_{proj['id']}"):
                    st.session_state.editing_project = proj
                    st.rerun()
                
                if manage_cols[2].button("삭제", key=f"delete_{proj['id']}"):
                    delete_project(proj['id'])
                    st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
                    if st.session_state.selected_project_id == proj['id']:
                        st.session_state.selected_project_id = None
                        st.session_state.selected_project_name = None
                        auto_save_settings()
                    st.rerun()
    
    else:
        # 카드 뷰
        cols = st.columns(3)
        for idx, proj in enumerate(projects):
            with cols[idx % 3]:
                is_selected = (st.session_state.selected_project_id == proj['id'])
                card_style = "border: 2px solid #1f77b4;" if is_selected else "border: 1px solid #ddd;"
                
                with st.container():
                    st.markdown(f"""
                    <div style="{card_style} padding: 10px; border-radius: 5px; margin: 5px 0;">
                        <h4>{proj['name']}</h4>
                        <p>{proj['description']}</p>
                        <small>ID: {proj['id']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    card_cols = st.columns(3)
                    if card_cols[0].button("✓" if is_selected else "선택", key=f"card_select_{proj['id']}", type="primary" if is_selected else "secondary"):
                        st.session_state.selected_project_id = proj['id']
                        st.session_state.selected_project_name = proj['name']
                        auto_save_settings()
                        st.rerun()
                    
                    if card_cols[1].button("수정", key=f"card_edit_{proj['id']}"):
                        st.session_state.editing_project = proj
                        st.rerun()
                    
                    if card_cols[2].button("삭제", key=f"card_delete_{proj['id']}"):
                        delete_project(proj['id'])
                        st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
                        if st.session_state.selected_project_id == proj['id']:
                            st.session_state.selected_project_id = None
                            st.session_state.selected_project_name = None
                            auto_save_settings()
                        st.rerun()

# --- 페이지 종료 시 설정 저장 ---
# 이 부분은 실제로는 작동하지 않지만, 개념적으로 보여주는 코드
# 실제로는 중요한 상태 변경 시점에 auto_save_settings()를 호출하는 것이 효과적
