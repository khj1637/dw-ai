import streamlit as st
# 페이지 기본 설정 (파일 제일 상단에 위치해야 함)
st.set_page_config(page_title="공사 예측 시스템", layout="wide")
import layout
from logisticstime import app as logistic_app
from workdayai import app as workday_app

# 페이지 기본 설정 (파일 제일 상단에 위치해야 함)
st.set_page_config(page_title="공사 예측 시스템", layout="wide")

# 스타일 및 레이아웃 불러오기
layout.load_css()
layout.header()

# URL 파라미터로 페이지 구분
query_params = st.query_params
page = query_params.get("page", ["home"])[0]

# 페이지 라우팅
if page == "logistic":
    logisticstime.app()
elif page == "workday":
    workdayai.app()
else:
    st.title("공사 예측 시스템 메인 페이지")
    st.markdown("원하는 기능을 상단 메뉴에서 선택하세요.")

layout.footer()
