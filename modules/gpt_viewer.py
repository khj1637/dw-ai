import streamlit as st
import openai
import json
from modules.form_fields import FIELD_DEFINITIONS
from modules.gpt_extract_fields import extract_defect_fields
from modules.save_utils import save_to_sheet

# 🔐 API 키 로딩
try:
    api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
except KeyError:
    st.error("❌ OpenAI API 키가 설정되어 있지 않습니다.")
    st.stop()

# 🔍 GPT 유형 분류
def classify_input_type(user_input, api_key):
    openai.api_key = api_key
    system_prompt = """
당신은 지식순환 시스템의 분류 전문가입니다.
사용자의 문장을 다음 중 하나로 분류해 주세요:
- 하자사례
- VE사례
- 공사기간
- 기타사례

형식은 반드시 JSON으로:
{
  "type": "하자사례" 또는 "VE사례" 또는 "공사기간" 또는 "기타사례",
  "message": "간단한 이유"
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
        return json.loads(response.choices[0].message["content"])
    except Exception as e:
        return {"type": "오류", "message": str(e)}

# 🧠 항목 추출
def extract_fields_by_type(user_input, case_type, api_key):
    if case_type == "하자사례":
        return extract_defect_fields(user_input, api_key)
    # elif case_type == "VE사례":
    #     return extract_ve_fields(user_input, api_key)
    else:
        return {"error": f"{case_type}에 대한 자동 추출 기능은 아직 구현되지 않았습니다."}

# 🧾 메인 GPT 챗봇
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 기반 등록)")

    # 세션 상태 초기화
    for key in ["chat_history", "current_type", "fields", "missing_fields", "field_index", "autofill_done"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key == "chat_history" or key == "missing_fields" else None if key in ["current_type"] else 0 if key == "field_index" else False

    # 대화 기록 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력창
    user_input = st.chat_input("자연어로 사례를 입력해 주세요.")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # 1단계: GPT 분류
        if not st.session_state.current_type:
            result = classify_input_type(user_input, api_key)
            st.session_state.current_type = result["type"]

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"**[{result['type']}]** {result['message']}"
            })

            with st.spinner("📂 항목 자동 추출 중..."):
                autofill = extract_fields_by_type(user_input, result["type"], api_key)

            if "error" in autofill:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ 오류: {autofill['error']}"
                })
                return

            st.session_state.fields = autofill
            st.session_state.autofill_done = True

            required = FIELD_DEFINITIONS.get(result["type"], [])
            st.session_state.missing_fields = [f for f in required if not autofill.get(f)]

        # 2단계: 누락 항목 입력받기
        elif st.session_state.missing_fields:
            current_field = st.session_state.missing_fields[st.session_state.field_index]
            st.session_state.fields[current_field] = user_input
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"✅ `{current_field}` 입력 완료."
            })
            st.session_state.field_index += 1

            if st.session_state.field_index >= len(st.session_state.missing_fields):
                st.session_state.missing_fields = []

        st.experimental_rerun()

    # 누락 항목 질문
    if st.session_state.autofill_done and st.session_state.missing_fields:
        field = st.session_state.missing_fields[st.session_state.field_index]
        with st.chat_message("assistant"):
            st.markdown(f"❓ `{field}` 값을 입력해 주세요.")

    # 모든 항목이 입력되었을 때 저장
    if st.session_state.autofill_done and not st.session_state.missing_fields:
        with st.chat_message("assistant"):
            st.success("✅ 모든 정보가 입력되었습니다. 저장하시겠습니까?")
            if st.button("📥 저장하기"):
                case_type = st.session_state.current_type
                worksheet_map = {
                    "하자사례": "defect_cases",
                    "VE사례": "ve_cases",
                    "공사기간": "construction",
                    "기타사례": "misc_cases"
                }
                save_to_sheet("knowledge_db", worksheet_map[case_type], st.session_state.fields)

                st.success("🎉 구글 시트에 저장되었습니다!")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "📌 사례가 저장되었습니다. 새로운 입력을 시작하려면 초기화 해 주세요."
                })

    # 🔄 새로 시작
    if st.button("🔄 새로 시작"):
        for key in ["chat_history", "current_type", "fields", "missing_fields", "field_index", "autofill_done"]:
            st.session_state.pop(key, None)
        st.experimental_rerun()
