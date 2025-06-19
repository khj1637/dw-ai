import streamlit as st
import json
from openai import OpenAI
from modules.form_fields import FIELD_DEFINITIONS
from modules.gpt_extract_fields import extract_defect_fields, classify_input_type
from modules.save_utils import save_to_sheet
from modules.form_fields import FIELD_DEFINITIONS, FIELD_QUESTIONS


# 💬 자연어 기반 대화형 하자사례 입력 전용 GPT 처리 함수
def render_gpt_viewer():
    # 🔐 OpenAI API 키 로딩
    try:
        api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
    except KeyError:
        st.error("❌ OpenAI API 키가 설정되어 있지 않습니다.")
        st.stop()

    # 🔍 필드별 질문 정의
    FIELD_QUESTIONS = {
        "현장명": "어느 현장에서 발생한 사례인가요?",
        "발생일": "이 사례는 언제 발생했나요?",
        "공종": "어떤 공종에서 발생한 문제인가요?",
        "사례 결과": "이 사례는 성공사례인가요, 실패사례인가요?",
        "하자 내용": "어떤 하자가 발생했는지 알려주세요.",
        "상세 내용": "그 상황에 대해 좀 더 구체적으로 설명해 주세요.",
        "해결 방안": "문제를 어떻게 해결하셨나요?",
        "실패 원인": "실패한 원인이 무엇이었다고 생각하시나요?"
    }

    # ✅ 상태 초기화
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

    # ✅ 채팅 기록 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ✅ 사용자 입력 받기
    user_input = st.chat_input("자연어로 사례를 자유롭게 말씀해 주세요.")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # ✅ 저장 여부 응답
        if st.session_state.awaiting_confirmation and not st.session_state.user_confirmed_save:
            if user_input.strip().lower() in ["네", "예", "좋아요", "등록해", "저장해", "ㅇㅇ", "ok", "넵"]:
                st.session_state.user_confirmed_save = True
                st.rerun()
                return

        # ✅ 초기 입력: 유형 분류 및 하자사례 추출
        if st.session_state.current_type is None:
            result = classify_input_type(user_input, api_key)
            if result["type"] != "하자사례":
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"📌 이 시스템은 현재 하자사례만 지원합니다.\n\n입력하신 내용은 '{result['type']}'로 분류되었습니다."
                })
                st.rerun()

            st.session_state.current_type = "하자사례"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"✅ 하자사례로 분류했습니다. 내용을 바탕으로 항목을 추출해 볼게요."
            })

            with st.spinner("🧠 내용을 분석하고 있어요..."):
                autofill = extract_defect_fields(user_input, api_key)

            if "error" in autofill:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ 항목 추출 중 오류가 발생했어요:\n{autofill['error']}"
                })
                st.rerun()

            st.session_state.fields = autofill
            st.session_state.autofill_done = True

            required_fields = FIELD_DEFINITIONS["하자사례"]
            st.session_state.missing_fields = [
                f for f in required_fields if not autofill.get(f)
            ]
            st.session_state.field_index = 0

            if st.session_state.missing_fields:
                first_field = st.session_state.missing_fields[0]
                question = FIELD_QUESTIONS.get(first_field, f"{first_field} 값을 입력해 주세요.")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"🙋 {question}"
                })
            else:
                st.rerun()

        # ✅ 누락 항목 대화형 질문
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
                    "content": f"좋아요! 다음으로 {question}"
                })
                st.rerun()

    # ✅ 최종 저장 여부 질문
    if st.session_state.autofill_done and not st.session_state.missing_fields:
        if not st.session_state.awaiting_confirmation:
            summary = "\n".join([
                f"- **{k}**: {v}" for k, v in st.session_state.fields.items() if v
            ])
            with st.chat_message("assistant"):
                st.markdown(f"📋 아래와 같이 정리했어요. 이대로 저장할까요?\n\n{summary}")
            st.session_state.awaiting_confirmation = True
            st.rerun()

    # ✅ 저장 실행
    if st.session_state.user_confirmed_save:
        with st.chat_message("assistant"):
            save_to_sheet("knowledge_db", "defect_cases", st.session_state.fields)
            st.success("✅ 하자사례가 저장되었습니다.")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "🎉 저장이 완료되었습니다! 새 사례를 입력하려면 🔄 새로 시작을 눌러주세요."
            })

        for key in [
            "current_type", "fields", "missing_fields", "field_index",
            "autofill_done", "awaiting_confirmation", "user_confirmed_save"
        ]:
            st.session_state.pop(key, None)
        st.rerun()

    # 🔁 초기화 버튼
    if st.button("🔄 새로 시작"):
        for key in [
            "chat_history", "current_type", "fields", "missing_fields", "field_index",
            "autofill_done", "awaiting_confirmation", "user_confirmed_save"
        ]:
            st.session_state.pop(key, None)
        st.rerun()
