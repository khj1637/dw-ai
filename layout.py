import streamlit as st

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def header():
    st.markdown("""
    <div class="fixed-header">
        <div class="logo-area">
            <img src="https://raw.githubusercontent.com/khj1637/dw-workday-ai/main/img/logo.png" width="140">
        </div>
        <div class="menu-area">
            <a href="/" class="menu-item" target="_self">Home</a>
            <a href="/?page=logistic" class="menu-item" target="_self">물류센터 공기예측</a>
            <a href="/?page=workday" class="menu-item" target="_self">공사가동률 계산</a>
        </div>
    </div>
    <div style="margin-top: 140px;"></div>
    """, unsafe_allow_html=True)

def footer():
    st.markdown("""
    <div class="footer">
        <div class="footer-content">
            <p>ⓒ 2025 동원건설산업 기술팀</p>
            <p>이메일: <a href="mailto:hyukjin@dwci.co.kr">hyukjin@dwci.co.kr</a></p>
            <p>주소: 서울특별시 강남구 테헤란로 123</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
