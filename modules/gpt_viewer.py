import streamlit as st
import datetime
from modules.gpt_extract_fields import extract_defect_fields  # 추후 활용
from modules.save_utils import save_to_sheet
import openai

# GPT 유형 분류 함수
def classify_input_type(user_input, api_key):
    openai.api_key = api_key

    system_prompt = """
다음 사용자 문장을 분석해서 아래 유형 중 하나로 분류하세요:
- 하자사례
- VE사례
- 일반 질문 (저장 불필요)

출력 형식은 반드시 JSON으로:
{
  "type": "하자사례" 또는 "VE사례" 또는 "일반 질문",
  "message": "분류에 대한 간단한 설명 또는 요약"
}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3
    )

    content = response.choices[0].message["content"]
    try:
        result = eval(content.strip())  # 안전한 버전은 json.loads 사용
        return result
    except Exception as e:
        return {"type": "오류", "message": str(e)}

# 메인 뷰어
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 챗봇)")
    api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("궁금한 점이나 사례를 자유롭게 입력하세요.")
    if user_input and api_key:
        # 사용자 메시지 저장
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # GPT 분류
        with st.spinner("GPT가 분석 중입니다..."):
            result = classify_input_type(user_input, api_key)

        # GPT 응답 저장
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"[{result['type']}] {result['message']}"
        })

        # 이후 단계 분기 준비
        if result["type"] == "하자사례":
            st.session_state.register_type = "defect"
        elif result["type"] == "VE사례":
            st.session_state.register_type = "ve"
        else:
            st.session_state.register_type = None

        st.experimental_rerun()

    # 채팅 이력 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 다음 흐름 안내
    if st.session_state.get("register_type") == "defect":
        st.info("➡️ GPT가 하자사례로 판단했습니다. 항목 추출 및 저장 화면으로 전환합니다.")
        # 여기에 render_defect_flow() 등 연결 가능
    elif st.session_state.get("register_type") == "ve":
        st.info("➡️ GPT가 VE사례로 판단했습니다. VE 등록 화면으로 전환합니다.")
        # 추후 render_ve_flow() 연결
