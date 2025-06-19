import streamlit as st
import json
from openai import OpenAI
from modules.form_fields import FIELD_DEFINITIONS
from modules.gpt_extract_fields import extract_defect_fields
from modules.save_utils import save_to_sheet

# 🔐 OpenAI API 키 로딩 및 클라이언트 객체 생성
try:
    api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except KeyError:
    st.error("❌ OpenAI API 키가 설정되어 있지 않습니다.")
    st.stop()

# 🔍 GPT 유형 분류 함수
def classify_input_type(user_input):
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
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"type": "오류", "message": f"GPT 응답 오류: {str(e)}"}
    except Exception as e:
        return {"type": "오류", "message": str(e)}

# ✨ 유형별 항목 추출 함수 (하자사례만)
def extract_fields_by_type(user_input, case_type):
    if case_type == "하자사례":
        return extract_defect_fields(user_input, api_key)
    else:
        return {"error": f"{case_type} 유형은 현재 자동 추출 기능이 준비 중입니다."}

# 💬 메인 챗봇 인터페이스
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 기반 등록)")

    # ✅ 세션 초기화
    for key, default in {
        "chat_history": [],
        "current_type": None,
        "fields": {},
        "missing_fields": [],
        "field_index": 0,
        "autofill_done": False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ✅ 대화 이력 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ✅ 입력창
    user_input = st.chat_input("자연어로 사례를 입력해 주세요.")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # 1️⃣ 첫 입력 → 유형 분류 + 항목 추출
        if st.session_state.current_type is None:
            result = classify_input_type(user_input)
            st.session_state.current_type = result["type"]
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"**[{result['type']}]** {result['message']}"
            })

            with st.spinner("🧠 GPT가 항목을 추출 중입니다..."):
                autofill = extract_fields_by_type(user_input, result["type"])

            if "error" in autofill:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ 오류: {autofill['error']}"
                })
                st.rerun()

            st.session_state.fields = autofill
            st.session_state.autofill_done = True

            required = FIELD_DEFINITIONS.get(result["type"], [])
            st.session_state.missing_fields = [f for f in required if not autofill.get(f)]
            st.rerun()

        # 2️⃣ 누락 항목 수동 입력
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
            st.rerun()

    # ❓ 누락 항목 입력 요청
    if st.session_state.autofill_done and st.session_state.missing_fields:
        field = st.session_state.missing_fields[st.session_state.field_index]
        with st.chat_message("assistant"):
            st.markdown(f"❓ `{field}` 값을 입력해 주세요.")

    # 💾 저장
    if st.session_state.autofill_done and not st.session_state.missing_fields:
        with st.chat_message("assistant"):
            st.success("✅ 모든 항목이 입력되었습니다. 저장하시겠습니까?")
            if st.button("📥 저장하기"):
                worksheet_map = {
                    "하자사례": "defect_cases",
                    "VE사례": "ve_cases",
                    "공사기간": "construction",
                    "기타사례": "misc_cases"
                }
                sheet = worksheet_map.get(st.session_state.current_type)
                save_to_sheet("knowledge_db", sheet, st.session_state.fields)

                st.success("🎉 구글 시트에 저장 완료!")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "✅ 저장 완료! 새로 시작하려면 🔄 버튼을 눌러주세요."
                })

    # 🔁 초기화 버튼
    if st.button("🔄 새로 시작"):
        for key in ["chat_history", "current_type", "fields", "missing_fields", "field_index", "autofill_done"]:
            st.session_state.pop(key, None)
        st.rerun()
