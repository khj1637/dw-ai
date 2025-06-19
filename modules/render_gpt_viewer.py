from modules.gpt_extract_fields import extract_defect_fields

def render_gpt_viewer():
    st.subheader("🧠 지식순환 GPT (정보 등록)")

    api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else st.text_input("OpenAI API Key", type="password")

    if "step" not in st.session_state:
        st.session_state.step = 0

    if st.session_state.step == 0:
        user_input = st.text_area("하자사례를 자연어로 입력해주세요.")
        if st.button("처리 시작") and user_input and api_key:
            with st.spinner("GPT가 항목을 추출 중입니다..."):
                result = extract_defect_fields(user_input, api_key)
                if "error" in result:
                    st.error("오류 발생: " + result["error"])
                    return

                # 항목들을 세션에 저장
                for key, value in result.items():
                    st.session_state[key] = value
                st.session_state.step = 1
                st.experimental_rerun()
