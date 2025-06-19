import streamlit as st
import openai
import datetime
from modules.gpt_extract_fields import extract_defect_fields  # (차후 활용 예정)
from modules.save_utils import save_to_sheet

# ✅ GPT 유형 분류 함수
def classify_input_type(user_input, api_key):
    openai.api_key = api_key

    system_prompt = """
당신은 지식순환 시스템을 위한 분류 전문가입니다.
사용자의 자연어 입력을 아래의 세 가지 유형 중 하나로 분류해 주세요:
- 하자사례
- VE사례
- 일반 질문 (저장 불필요)

그리고 해당 판단에 대한 간단한 이유나 요약도 함께 주세요.

💬 출력은 반드시 JSON 형식으로 반환해 주세요:
{
  "type": "하자사례" 또는 "VE사례" 또는 "일반 질문",
  "message": "이유나 간단 요약"
}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3
        )
        content = response.choices[0].message["content"]
        result = eval(content.strip())  # ⚠️ 배포용은 json.loads()로 보안 강화 권장
        return result
    except Exception as e:
        return {"type": "오류", "message": str(e)}

# ✅ 메인 챗봇 인터페이스
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 챗봇)")

    # ✅ OpenAI API 키 설정
    api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")

    # ✅ 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "register_type" not in st.session_state:
        st.session_state.register_type = None

    # ✅ 기존 대화 내용 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ✅ 사용자 입력 받기 (맨 마지막에 위치해야 하단 고정됨)
    user_input = st.chat_input("궁금한 점이나 사례를 자연어로 입력해보세요.")
    if user_input and api_key:
        # 사용자 메시지 저장
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # GPT 분류
        with st.spinner("GPT가 입력을 분석 중입니다..."):
            result = classify_input_type(user_input, api_key)

        # GPT 응답 저장
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"**[{result['type']}]** {result['message']}"
        })

        # 유형 분류 결과 저장
        if result["type"] == "하자사례":
            st.session_state.register_type = "defect"
        elif result["type"] == "VE사례":
            st.session_state.register_type = "ve"
        else:
            st.session_state.register_type = None

        # 화면 갱신
        st.experimental_rerun()

    # ✅ 다음 단계 안내
    if st.session_state.register_type == "defect":
        st.info("➡️ GPT가 이 입력을 **하자사례**로 분류했습니다. 항목 추출 및 등록 절차로 전환합니다.")
        # TODO: render_defect_flow() 등 연결 예정
    elif st.session_state.register_type == "ve":
        st.info("➡️ GPT가 이 입력을 **VE사례**로 분류했습니다. VE 등록 절차로 전환합니다.")
        # TODO: render_ve_flow() 등 연결 예정
