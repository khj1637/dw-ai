import streamlit as st
st.set_page_config(page_title="공사 예측 시스템", layout="wide")  # 가장 먼저 실행

import layout
import logisticstime
import workdayai

layout.load_css()
layout.header()

# 쿼리 파라미터에서 page 선택
page = st.query_params.get("page", "home")

# 해당 앱 실행
if page == "logistic":
    logisticstime.app()
elif page == "workday":
    workdayai.app()
else:
    st.title("공사 예측 시스템 메인")
    st.write("왼쪽 메뉴 또는 상단 메뉴에서 기능을 선택하세요.")

layout.footer()
