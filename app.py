import streamlit as st
from modules.input_forms import (
    render_defect_form,
    render_ve_form,
    render_duration_form,
    render_etc_form
)

# 👉 Google Sheet 기본 설정
SHEET_NAMES = {
    "defect": "knowledge_db",
    "ve": "ve_data",
    "duration": "construction",
    "etc": "misc_cases"
}

SHEET_TABS = {
    "defect": "하자사례",
    "ve": "VE사례",
    "duration": "공사기간",
    "etc": "기타사례"
}

# ✅ Streamlit 앱 설정
st.set_page_config(page_title="지식순환 시스템", layout="wide")
st.title("🏗️ 지식순환 시스템 (Google Sheets 연동)")

# ✅ 탭 구성
tab1, tab2, tab3, tab4 = st.tabs([
    "🔧 하자사례",
    "💡 VE사례",
    "📅 공사기간",
    "📁 기타사례"
])

# ✅ 각 탭에서 입력 폼 호출
with tab1:
    render_defect_form(SHEET_NAMES["defect"], SHEET_TABS["defect"])

with tab2:
    render_ve_form(SHEET_NAMES["ve"], SHEET_TABS["ve"])

with tab3:
    render_duration_form(SHEET_NAMES["duration"], SHEET_TABS["duration"])

with tab4:
    render_etc_form(SHEET_NAMES["etc"], SHEET_TABS["etc"])