import streamlit as st
from modules.input_forms import (
    render_defect_form,
    render_ve_form,
    render_duration_form,
    render_etc_form
)

# 👉 Google Sheet 기본 설정
SHEET_NAME = "streamlit-knowledge-db"  # 구글 스프레드시트 문서명 또는 문서 ID
SHEET_TABS = {
    "defect": "Sheet1",      # 하자사례
    "ve": "Sheet1",          # VE사례
    "duration": "Sheet1",    # 공사기간
    "etc": "Sheet1"           # 기타사례
}

# ✅ Streamlit 앱 설정
st.set_page_config(page_title="지식순환 시스템", layout="wide")
st.title("🏗️ 지식순환 시스템 (Google Sheets 연동)")

# ✅ 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["🔧 하자사례", "💡 VE사례", "📅 공사기간", "📁 기타사례"])

# ✅ 각 탭별 입력폼 호출
with tab1:
    render_defect_form("knowledge_db", SHEET_TABS["defect"])

with tab2:
    render_ve_form("ve_data", SHEET_TABS["ve"])

with tab3:
    render_duration_form("construction", SHEET_TABS["duration"])

with tab4:
    render_etc_form("misc_cases", SHEET_TABS["etc"])
