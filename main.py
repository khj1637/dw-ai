import streamlit as st

# 페이지 설정은 반드시 최상단
st.set_page_config(page_title="공사 예측 시스템", layout="wide")

# 모듈 import
import layout
from logisticstime import run_logisticstime
from workdayai import run_workdayai



# 공통 CSS 및 레이아웃 로드
layout.load_css()
layout.header()

# URL 파라미터에서 page 값 가져오기
query_params = st.query_params
page = query_params.get("page", ["home"])[0]

# 라우팅
if page == "logistic":
    logisticstime.app()
elif page == "workday":
    workdayai.app()
else:
    st.title("📦 공사 예측 시스템 홈페이지")
    st.markdown("""
    공사 가동률 분석과 물류센터 예상 공기 산출을 한 곳에서 관리할 수 있는 통합 플랫폼입니다.
    좌측 상단 메뉴 또는 상단 링크를 클릭하여 기능을 선택하세요.
    """)

layout.footer()
