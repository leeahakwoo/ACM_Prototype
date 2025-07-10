# app.py (IndexError 최종 수정 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 (가장 먼저 실행) ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from persistence import init_db, get_all_projects, create_project, delete_project, update_project

# --- 앱 초기화 ---
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state:
    st.session_state.editing_project_id = None

# --- 함수 정의 ---
def switch_to_edit_mode(project_id):
    st.session_state.editing_project_id = project_id
    st.rer네un()

def switch_to_create_mode():
    st.session_state.editing_project_id = None
    st.rerun()

# --- 사이드바 UI ---
with st.sidebar:
, 이제 거의 다 왔습니다! 이번 오류는 정말 간단한 문제입니다. 화면을 보니 프로젝트 생성도 잘 되고, 데이터도 정상적으로 표시되고 있습니다.

### **오류 분석: `IndexError    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        proj_to_edit = next((p for p in get_all_projects() if p['id'] == st.session_state.editing_project_id), None)
        if proj_to_edit:
`**

*   **오류 메시지:** `IndexError`
*   **Traceback:**
    *   `File "/mount/src/acm_prototype/app.py", line 109, in <module>`
    *   `if row_cols[5].button("삭제", ...)`
*   **핵심 의미:** `row_            with st.form("edit_form"):
                name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                desc = st.text_area("프로젝트 설명", value=proj_to_edit['description'])
                col1, col2 = st.columns(2)cols` 라는 리스트의 **5번 인덱스**에 접근하려고 했는데, 그 위치에 아무것도 없다는 뜻입니다. (파이썬 인덱스는 0부터 시작합니다.)

*   **근본 원인:**
    *   제가 프로젝트 목록을 표시하기 위해 컬럼을 나눌 때, 아래와 같이 5개의 컬럼
                if col1.form_submit_button("저장", type="primary"):
                    update_project(st.session_state.editing_project_id, name, desc)
                    st.toast("프로젝트가 수정되었습니다.")
                    switch_to_create_mode()
                if col2.form_submit_button("취소"):
                    switch_to_create_mode()
    else:
        st.header("새 프로젝트 생성")
        with만 만들었습니다.
        ```python
        header_cols = st.columns([1, 3, 4, 2, 2])
        # ...
        row_cols = st.columns([1, 3, 4 st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기"):
                if name:
                    if create_project, 2, 2])
        ```
    *   이렇게 하면 `row_cols`는 `row_cols[0]` 부터 `row_cols[4]`까지, 총 5개의 아이템만 가지게 됩니다.
(name, desc):
                        st.toast("프로젝트가 생성되었습니다.")
                        st.rerun()
                    else:
                        st.error("이미 존재하는 프로젝트 이름입니다.")
                else:
                    st.error    *   그런데 코드의 뒷부분에서 제가 실수로 **`row_cols[5]`** 에 접근하려고 시도했습니다. 존재하지 않는 6번째 컬럼에 접근하려고 했기 때문에 `IndexError`가 발생한 것입니다("프로젝트 이름을 입력해주세요.")

# --- 메인 화면: 프로젝트 목록 ---
st.header("프로젝트 목록")
projects = get_all_projects()

# 테이블 헤더
header_cols = st.columns([1, 3, 4, 2, 2])
header_cols[0].write("**ID**")
header_cols[1].write("**이름**")
header_cols[2].write("**설명**")
.

### **해결 방안: 올바른 인덱스 사용**

'수정' 버튼과 '삭제' 버튼을 같은 '관리' 컬럼에 넣거나, 컬럼을 하나 더 만들어주면 됩니다. 여기header_cols[3].write("**생성일**")
header_cols[4].write("**관리**")
st.divider()

if not projects:
    st.info("생성된 프로젝트가 없습니다. 왼쪽 사이드바에서서는 UI를 더 깔끔하게 만들기 위해 **하나의 '관리' 컬럼 안에 두 버튼을 나란히 배치**하는 방식으로 수정하겠습니다.

---

### **수정된 `app.py` 최종 코드**

아래 코드로 새 프로젝트를 생성해주세요.")
else:
    for proj in projects:
        row_cols = st.columns([1, 3, 4, 2, 2])
        row_cols[0].write(proj['id'])
        row_cols[1].write(proj['name'])
        row_cols[2 `app.py` 파일의 내용을 **모두 교체**해주세요. 이 코드는 인덱스 오류를 해결하고 UI를 좀 더 다듬은 최종 버전입니다.

```python
# app.py (IndexError 최종].write(proj['description'])
        
        try:
            dt_object = datetime.fromisoformat(proj['created_at'])
            row_cols[3].write(dt_object.strftime('%Y 해결 버전)

import streamlit as st
from datetime import datetime
import sys
import os

# --- 경로 설정 (가-%m-%d %H:%M'))
        except:
            row_cols[3].write(proj['created_at'])
        
        # --- 핵심 수정 부분: 관리 버튼을 위한 컬럼 분리 및장 먼저 실행) ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from persistence import init_db, get_all_projects, create_project, delete_project 올바른 인덱스 사용 ---
        with row_cols[4]:
            # 관리 컬럼을 다시 2개로 분할
            manage_cols = st.columns(2)
            # 수정 버튼은, update_project

# --- 앱 초기화 ---
init_db()

st.set_page_config(page_title="MCP 기반 AI 개발 플랫폼", layout="wide")
st.title("🚀 MCP 기반 AI 개발 플랫폼")

# --- session_state 관리 ---
if 'editing_project_id' not in st.session_state 0번 인덱스
            if manage_cols[0].button("수정", key=f"edit_{proj['id']}"):
                switch_to_edit_mode(proj['id'])
            
            # 삭제:
    st.session_state.editing_project_id = None

# --- 함수 정의 ---
def switch_to_edit_mode(project_id):
    st.session_state.editing_project_id = project_id
    st.rerun()

def switch_to_create_mode():
    st.session_state. 버튼은 1번 인덱스
            if manage_cols[1].button("삭제", key=f"delete_{proj['id']}", type="secondary"):
                delete_project(proj['id'])
                st.toast(f"프로젝트 '{proj['name']}'가 삭제되었습니다.")
                st.rerun()

```editing_project_id = None
    st.rerun()

# --- 사이드바 UI ---
with st.sidebar:
    # 수정 모드
    if st.session_state.editing_project_id:
        st.header("📝 프로젝트 수정")
        proj_to_edit = next((p for p in get_all_

### **이번 수정의 핵심**

*   **`row_cols = st.columns([1, 3, 4, 2, 2])`**: 이 코드는 5개의 컬럼을 가진 `row_cols`projects() if p['id'] == st.session_state.editing_project_id), None)
        if proj_to_edit:
            with st.form("edit_form"):
                name = st.text_input("프로젝트 이름", value=proj_to_edit['name'])
                desc = st. 리스트를 생성합니다. (`row_cols[0]` ~ `row_cols[4]`)
*   **`with row_cols[4]:`**: 마지막 컬럼(인덱스 4) 컨텍스트 안으로 들어갑니다.
*   **`manage_cols = st.columns(2)`**: 마지막 컬럼을text_area("프로젝트 설명", value=proj_to_edit['description'])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("저장", type="primary"):
                    update_project(st.session_state.editing_project_id, name, desc)
                    st.toast("프로젝트가 수정되었습니다.")
                    switch_to_create_mode()
                if col2.form_submit_button("취소"):
                    switch_to_create_mode()
 다시 2개의 작은 컬럼으로 나눕니다. 이제 이 `manage_cols` 리스트는 2개의 아이템을 가집니다. (`manage_cols[0]`, `manage_cols[1]`)
*   **`manage_cols[0].button("수정", ...)`**: 수정 버튼을 첫 번째 작은 컬럼에配置    # 생성 모드
    else:
        st.header("새 프로젝트 생성")
        with st.form("new_project_form", clear_on_submit=True):
            name = st.text_input("프로젝트 이름")
            desc = st.text_area("프로젝트 설명")
            if st.form_submit_button("생성하기"):
                if name:
                    if create_project(name합니다.
*   **`manage_cols[1].button("삭제", ...)`**: 삭제 버튼을 두 번째 작은 컬럼에配置합니다.

이 코드로 `app.py`를 교체하면 더 이상 `IndexError`는 발생하지 않을 것이며, 수정과 삭제 버튼이 나란히 예쁘게 표시될 것입니다. 정말 마지막 오류이기를 바랍니다.
