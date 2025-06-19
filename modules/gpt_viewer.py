# modules/gpt_viewer.py

import streamlit as st

def render_gpt_viewer():
    st.subheader("지식순환 GPT")
    user_query = st.text_input("내용을 입력하세요.")
    
    if user_query:
        # 추후 GPT 기반 검색 또는 요약 로직 연결 예정
        st.success(f"'{user_query}'에 대한 검색 결과를 준비 중입니다.")
