import streamlit as st
from modules.input_forms import (
    render_defect_form,
    render_ve_form,
    render_duration_form,
    render_etc_form
)
from modules.gpt_viewer import render_gpt_viewer  # 🆕 새로 추가할 GPT 화면 함수

# ✅ Google Sheets 문서명
SHEET_NAME = "knowledge_db"

# ✅ 워크시트 이름
SHEET_TABS = {
    "defect": "defect_cases",
    "ve": "ve_cases",
    "duration": "construction",
    "etc": "misc_cases"
}

# ✅ Streamlit 설정
st.set_page_config(page_title="지식순환 시스템", layout="wide")
st.title("AI기반 지식순환 시스템")

# ✅ 탭 구성 (GPT 탭 포함)
tab_gpt, tab1, tab2, tab3, tab4 = st.tabs([
    "지식순환 GPT",  # 🆕 맨 왼쪽 탭
    "하자사례 등록",
    "VE사례 등록",
    "공사기간 정보등록",
    "기타사례 등록"
])

# ✅ 탭별 콘텐츠 연결
with tab_gpt:
    render_gpt_viewer()  # 🆕 GPT 기능 또는 화면

with tab1:
    render_defect_form(SHEET_NAME, SHEET_TABS["defect"])

with tab2:
    render_ve_form(SHEET_NAME, SHEET_TABS["ve"])

with tab3:
    render_duration_form(SHEET_NAME, SHEET_TABS["duration"])

with tab4:
    render_etc_form(SHEET_NAME, SHEET_TABS["etc"])
