import streamlit as st
from modules.input_forms import (
    render_defect_form,
    render_ve_form,
    render_duration_form,
    render_etc_form
)
from modules.gpt_autofill import render_autofill  # 🧠 지식순환 GPT 탭 함수

# ✅ Google Sheets 문서명 (모든 워크시트가 이 문서 안에 있음)
SHEET_NAME = "knowledge_db"

# ✅ 시트 이름 매핑
SHEET_TABS = {
    "defect": "defect_cases",
    "ve": "ve_cases",
    "duration": "construction",
    "etc": "misc_cases"
}

# ✅ Streamlit 앱 기본 설정
st.set_page_config(page_title="지식순환 시스템", layout="wide")
st.title("📚 AI 기반 지식순환 시스템")

# ✅ 탭 구성: GPT 탭 + 수동 입력 탭들
tab_gpt, tab1, tab2, tab3, tab4 = st.tabs([
    "지식순환 GPT",          # 🧠 대화형 입력 (자연어 기반)
    "하자사례 등록",         # 📝 수동 입력
    "VE사례 등록",          # 📝 수동 입력
    "공사기간 정보등록",     # 📝 수동 입력
    "기타사례 등록"         # 📝 수동 입력
])

# ✅ 각 탭별 콘텐츠 연결
with tab_gpt:
    render_gpt_viewer()  # 챗봇 기반 자동 입력 시작

with tab1:
    render_defect_form(SHEET_NAME, SHEET_TABS["defect"])

with tab2:
    render_ve_form(SHEET_NAME, SHEET_TABS["ve"])

with tab3:
    render_duration_form(SHEET_NAME, SHEET_TABS["duration"])

with tab4:
    render_etc_form(SHEET_NAME, SHEET_TABS["etc"])
