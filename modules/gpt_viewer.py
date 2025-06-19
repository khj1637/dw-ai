import streamlit as st
import json
from openai import OpenAI
from modules.form_fields import FIELD_DEFINITIONS
from modules.gpt_extract_fields import extract_defect_fields, classify_input_type
from modules.save_utils import save_to_sheet

def render_gpt_viewer():
    # 🔐 API 키 로딩 및 클라이언트 생성
    try:
        api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
    except KeyError:
        st.error("❌ OpenAI API 키가 설정되어 있지 않습니다.")
        st.stop()

    # ✅ 세션 상태 초기화
    default_state = {
        "chat_history": [],
        "current_type": None,
        "fields": {},
        "missing_fields": [],
        "autofill_done": False,
        "awaiting_confirmation": False,
        "user_confirmed_save": False
    }
    for key, val in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # 💬 대화 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 📥 사용자 입력
    user_input = st.chat_input("자연어로 사례를 입력해 주세요.")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # ✅ 저장 관련 자연어 명령 감지
        if any(k in user_input.lower() for k in ["저장", "끝", "완료", "됐", "등록"]):
            if st.session_state.missing_fields:
                with st.chat_message("assistant"):
                    st.markdown(f"⚠️ 아직 입력되지 않은 항목이 있어요: `{', '.join(st.session_state.missing_fields)}`")
                return
            else:
                st.session_state.awaiting_confirmation = True
                st.rerun()

        # ✅ 첫 입력 처리 (유형 분류 + 필드 추출)
        if st.session_state.current_type is None:
            result = classify_input_type(user_input, api_key)
            st.session_state.current_type = result["type"]
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"✅ `{result['type']}`로 분류했습니다. 내용을 분석해서 항목을 추출해 볼게요."
            })

            with st.spinner("🧠 항목 분석 중..."):
                autofill = extract_defect_fields(user_input, api_key)

            if "error" in autofill:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ 오류 발생: {autofill['error']}"
                })
                return

            st.session_state.fields = autofill
            st.session_state.autofill_done = True

            required = FIELD_DEFINITIONS.get(result["type"], [])
            st.session_state.missing_fields = [f for f in required if not autofill.get(f)]

            # 🧾 요약 출력 + 다음 질문 유도
            filled_summary = '\n'.join(f"- **{k}**: {v}" for k, v in autofill.items() if v)
            if st.session_state.missing_fields:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"지금까지 입력된 내용입니다:\n\n{filled_summary}\n\n❓ 아직 `{', '.join(st.session_state.missing_fields)}` 항목이 입력되지 않았어요. 알려주세요!"
                })
            else:
                st.session_state.awaiting_confirmation = True
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"✅ 모든 항목이 입력되었습니다. 저장할까요?"
                })
            st.rerun()

        # ✅ 누락 항목 입력
        elif st.session_state.missing_fields:
            current_field = st.session_state.missing_fields.pop(0)
            st.session_state.fields[current_field] = user_input

            if st.session_state.missing_fields:
                next_field = st.session_state.missing_fields[0]
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"✅ `{current_field}` 항목이 등록되었습니다.\n이제 `{next_field}` 항목도 알려주세요."
                })
            else:
                st.session_state.awaiting_confirmation = True
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"✅ `{current_field}` 항목까지 입력 완료되었습니다.\n저장할까요?"
                })
            st.rerun()

    # ✅ 저장 승인 받기
    if st.session_state.awaiting_confirmation and not st.session_state.user_confirmed_save:
        with st.chat_message("assistant"):
            st.markdown("💬 저장을 원하시면 '네', '저장해' 등으로 답해주세요.")

    # ✅ 저장 승인 응답 처리
    if user_input and st.session_state.awaiting_confirmation:
        if user_input.strip().lower() in ["네", "예", "좋아요", "ㅇㅇ", "ok", "저장해"]:
            st.session_state.user_confirmed_save = True
            worksheet_map = {
                "하자사례": "defect_cases",
                "VE사례": "ve_cases",
                "공사기간": "construction",
                "기타사례": "misc_cases"
            }
            sheet = worksheet_map.get(st.session_state.current_type)
            save_to_sheet("knowledge_db", sheet, st.session_state.fields)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "🎉 사례가 저장되었습니다! 새로운 사례도 등록해보시겠어요?"
            })

            # 상태 초기화
            for key in default_state:
                st.session_state.pop(key, None)
            st.rerun()

    # 🔁 초기화 버튼
    if st.button("🔄 새로 시작"):
        for key in default_state:
            st.session_state.pop(key, None)
        st.rerun()