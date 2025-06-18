import streamlit as st
from modules.input_forms import (
    render_defect_form,
    render_ve_form,
    render_duration_form,
    render_etc_form
)
from modules.save_utils import init_csv
import os

# 앱 페이지 설정
st.set_page_config(page_title="지식순환 시스템", layout="wide")
st.title("🏗️ 지식순환 시스템")

# CSV 파일 경로 정의
FILE_PATHS = {
    "defect": "data/defect_cases.csv",
    "ve": "data/ve_cases.csv",
    "duration": "data/construction_duration.csv",
    "etc": "data/etc_cases.csv"
}

# 각 파일 초기화 (없으면 생성)
init_csv(FILE_PATHS["defect"], [
    "project", "date", "work_type", "result",
    "defect_content", "details", "solution", "fail_reason"
])
init_csv(FILE_PATHS["ve"], [
    "project", "date", "work_type", "result",
    "ve_content", "details", "effect", "fail_reason"
])
init_csv(FILE_PATHS["duration"], [
    "project", "usage", "structure", "land_area",
    "building_area", "total_floor_area",
    "above_ground", "underground", "height", "duration"
])
init_csv(FILE_PATHS["etc"], [
    "project", "date", "etc_content", "details"
])

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["🔧 하자사례", "💡 VE사례", "📅 공사기간", "📁 기타사례"])

# 탭별 입력폼 호출
with tab1:
    render_defect_form(FILE_PATHS["defect"])

with tab2:
    render_ve_form(FILE_PATHS["ve"])

with tab3:
    render_duration_form(FILE_PATHS["duration"])

with tab4:
    render_etc_form(FILE_PATHS["etc"])
