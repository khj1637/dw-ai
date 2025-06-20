import streamlit as st
from modules.input_forms import (
    render_defect_form,
    render_ve_form,
    render_duration_form,
    render_etc_form
)

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
st.set_page_config(page_title="동원건설산업 지식정보 저장소")
st.markdown(
    """
    <h1 style='text-align: center;'>Knowledge Collector</h1>
    <div style='height: 20px;'></div>  <!-- 공백 한 줄 -->
    <p style='text-align: left; font-size: 0.85rem; color: #555;'>
        버전: v1.0.0<br>
        최종 업데이트: 2025년 6월 17일<br>
        개발자 : 동원건설산업 기술팀 김혁진
    </p>
    """,
    unsafe_allow_html=True
)
# ✅ 탭 구성 (GPT 탭 포함)
tab1, tab2, tab3, tab4 = st.tabs([
    "하자사례 등록",
    "VE사례 등록",
    "공사기간 정보등록",
    "기타사례 등록"
])

with tab1:
    render_defect_form(SHEET_NAME, SHEET_TABS["defect"])

with tab2:
    render_ve_form(SHEET_NAME, SHEET_TABS["ve"])

with tab3:
    render_duration_form(SHEET_NAME, SHEET_TABS["duration"])

with tab4:
    render_etc_form(SHEET_NAME, SHEET_TABS["etc"])
