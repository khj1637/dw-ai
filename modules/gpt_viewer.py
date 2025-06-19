import streamlit as st
import json
from openai import OpenAI
from modules.form_fields import FIELD_DEFINITIONS
from modules.gpt_extract_fields import extract_defect_fields
from modules.save_utils import save_to_sheet

# 🔐 OpenAI API 키 로딩
try:
    api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except KeyError:
    st.error("❌ OpenAI API 키가 설정되어 있지 않습니다.")
    st.stop()

# 💬 필드별 자연어 질문 텍스트
FIELD_QUESTIONS = {
    "현장명": "어느 현장에서 발생한 사례인가요?",
    "발생일": "이 사례는 언제 발생했나요?",
    "공종": "어떤 공종에서 발생한 문제인가요?",
    "하자 내용": "어떤 하자가 발생했는지 말씀해 주세요.",
    "상세 내용": "그 상황을 좀 더 자세히 설명해 주실 수 있나요?",
    "해결 방안": "이 문제는 어떻게 해결하셨나요?",
    "실패 원인": "왜 이런 문제가 발생했다고 보시나요?"
}

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
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"type": "오류", "message": str(e)}

# ✨ 유형별 항목 추출
def extract_fields_by_type(user_input, case_type):
    if case_type == "하자사례":
        return extract_defect_fields(user_input, api_key)
    else:
        return {"error": f"{case_type} 유형은 현재 자동 추출 기능이 준비 중입니다."}

# 💬 메인 대화 인터페이스
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 대화 기반 사례 등록)")

    # 상태 초기화
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

    # 채팅 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력 받기
    user_input = st.chat_input("자연어로 사례를 입력해 주세요.")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # 저장 여부 응답 처리
        if st.session_state.awaiting_confirmation and not st.session_state.user_confirmed_save:
            if user_input.strip().lower() in ["네", "예", "좋아요", "등록해", "저장해", "ㅇㅇ", "ok", "넵"]:
                st.session_state.user_confirmed_save = True
                st.rerun()
                return

        # 첫 입력 → 유형 분류 및 자동 추출
        if st.session_state.current_type is None:
            result = classify_input_type(user_input)
            st.session_state.current_type = result["type"]
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"📂 입력 내용을 **[{result['type']}]**로 분류했어요.\n{result['message']}"
            })

            with st.spinner("🧠 사례 내용을 분석하고 있어요..."):
                autofill = extract_fields_by_type(user_input, result["type"])

            if "error" in autofill:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ 오류 발생: {autofill['error']}"
                })
                st.rerun()

            st.session_state.fields = autofill
            st.session_state.autofill_done = True

            required = FIELD_DEFINITIONS.get(result["type"], [])
            st.session_state.missing_fields = [f for f in required if not autofill.get(f)]

            # 첫 질문 던지기
            if st.session_state.missing_fields:
                first_field = st.session_state.missing_fields[0]
                question = FIELD_QUESTIONS.get(first_field, f"{first_field} 값을 입력해 주세요.")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"🙋 {question}"
                })
            st.rerun()

        # 누락 항목 수동 입력
        elif st.session_state.missing_fields:
            field = st.session_state.missing_fields[st.session_state.field_index]
            st.session_state.fields[field] = user_input

            st.session_state.field_index += 1
            if st.session_state.field_index >= len(st.session_state.missing_fields):
                st.session_state.missing_fields = []
                st.rerun()
            else:
                next_field = st.session_state.missing_fields[st.session_state.field_index]
                question = FIELD_QUESTIONS.get(next_field, f"{next_field} 값을 입력해 주세요.")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"👍 감사합니다! 이어서 {question}"
                })
                st.rerun()

    # 저장 여부 확인
    if st.session_state.autofill_done and not st.session_state.missing_fields:
        if not st.session_state.awaiting_confirmation:
            summary = "\n".join([f"- **{k}**: {v}" for k, v in st.session_state.fields.items()])
            with st.chat_message("assistant"):
                st.markdown(f"📋 아래와 같이 정리했어요. 저장할까요?\n\n{summary}")
            st.session_state.awaiting_confirmation = True
            st.rerun()

    # 저장 실행
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
                "content": "✅ 저장이 완료되었습니다. 새로운 사례를 입력하려면 🔄 새로 시작을 눌러주세요."
            })

        # 상태 초기화
        for key in ["current_type", "fields", "missing_fields", "field_index", "autofill_done", "awaiting_confirmation", "user_confirmed_save"]:
            st.session_state.pop(key, None)
        st.rerun()

    # 초기화 버튼
    if st.button("🔄 새로 시작"):
        for key in ["chat_history", "current_type", "fields", "missing_fields", "field_index", "autofill_done", "awaiting_confirmation", "user_confirmed_save"]:
            st.session_state.pop(key, None)
        st.rerun()
