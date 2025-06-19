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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        content = response.choices[0].message.content  # ✅ 이 부분이 핵심
        return json.loads(content)
    except Exception as e:
        return {"type": "오류", "message": str(e)}

# ✨ 유형별 항목 추출 함수 (하자사례만)
def extract_fields_by_type(user_input, case_type):
    if case_type == "하자사례":
        return extract_defect_fields(user_input, api_key)
    else:
        return {"error": f"{case_type} 유형은 현재 자동 추출 기능이 준비 중입니다."}

# 💬 메인 GPT 챗봇 인터페이스
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 기반 등록)")

    # ✅ 세션 초기화
    for key, default in {
        "chat_history": [],
        "current_type": None,
        "fields": {},
        "missing_fields": [],
        "field_index": 0,
        "autofill_done": False,
        "awaiting_confirmation": False,
        "user_confirmed_save": False
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

        # ✅ 사용자의 저장 승인 응답 처리
        if st.session_state.awaiting_confirmation and not st.session_state.user_confirmed_save:
            if user_input.strip().lower() in ["네", "예", "좋아요", "등록해", "저장해", "ㅇㅇ", "ok"]:
                st.session_state.user_confirmed_save = True
                st.rerun()
                return

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

    # ✅ 모든 입력이 완료되면 저장 여부 확인
    if st.session_state.autofill_done and not st.session_state.missing_fields:
        if not st.session_state.awaiting_confirmation:
            with st.chat_message("assistant"):
                st.markdown("✅ 모든 항목이 입력되었습니다. 이대로 저장할까요? (예: '네', '저장해')")
            st.session_state.awaiting_confirmation = True
            st.rerun()

    # 💾 실제 저장 실행
    if st.session_state.user_confirmed_save:
        with st.chat_message("assistant"):
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
                "content": "✅ 저장 완료! 새로운 입력을 원하시면 🔄 새로 시작을 눌러주세요."
            })

        for key in ["current_type", "fields", "missing_fields", "field_index", "autofill_done", "awaiting_confirmation", "user_confirmed_save"]:
            st.session_state.pop(key, None)
        st.rerun()

    # 🔁 초기화 버튼
    if st.button("🔄 새로 시작"):
        for key in ["chat_history", "current_type", "fields", "missing_fields", "field_index", "autofill_done", "awaiting_confirmation", "user_confirmed_save"]:
            st.session_state.pop(key, None)
        st.rerun()
