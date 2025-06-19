import streamlit as st
import openai
import datetime
import json
from modules.gpt_extract_fields import extract_defect_fields, classify_input_type
from modules.save_utils import save_to_sheet

# ✅ 챗봇 + 자동 항목 추출 통합 버전
def render_gpt_viewer():
    st.subheader("💬 지식순환 GPT (자연어 챗봇)")

    # ✅ OpenAI API 키 설정
    api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")

    # ✅ 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "register_type" not in st.session_state:
        st.session_state.register_type = None
    if "autofill_result" not in st.session_state:
        st.session_state.autofill_result = None

    # ✅ 기존 대화 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ✅ 사용자 입력
    user_input = st.chat_input("궁금한 점이나 사례를 자연어로 입력해보세요.")
    if user_input and api_key:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("GPT가 입력을 분석 중입니다..."):
            result = classify_input_type(user_input, api_key)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"**[{result['type']}]** {result['message']}"
        })

        # 분류 저장
        st.session_state.register_type = result["type"] if result["type"] in ["하자사례", "VE사례"] else None
        st.session_state.latest_user_input = user_input
        st.experimental_rerun()

    # ✅ 하자사례 처리 흐름
    if st.session_state.register_type == "하자사례":
        st.info("➡️ GPT가 이 입력을 **하자사례**로 분류했습니다. 항목을 자동 추출합니다.")

        if not st.session_state.autofill_result:
            with st.spinner("GPT가 항목을 추출 중입니다..."):
                result = extract_defect_fields(st.session_state.latest_user_input, api_key)
                if "error" in result:
                    st.error("❌ 오류: " + result["error"])
                    return
                st.session_state.autofill_result = result
                st.experimental_rerun()

        result = st.session_state.autofill_result

        # 사용자 보완 입력
        project = st.text_input("현장명", value=result.get("현장명", ""))
        date_val = st.date_input("발생일", value=datetime.date.today())
        work_type = st.text_input("공종", value=result.get("공종", ""))
        case_result = st.radio("사례 결과", ["성공사례", "실패사례"], index=0 if result.get("사례 결과") == "성공사례" else 1)
        defect_content = st.text_input("하자 내용", value=result.get("하자 내용", ""))
        details = st.text_area("상세 내용", value=result.get("상세 내용", ""))
        if case_result == "성공사례":
            solution = st.text_input("해결 방안", value=result.get("해결 방안", ""))
            fail_reason = ""
        else:
            solution = ""
            fail_reason = st.text_input("실패 원인", value=result.get("실패 원인", ""))

        if st.button("✅ 저장하기"):
            if not all([project, work_type, defect_content, details]) or (case_result == "성공사례" and not solution) or (case_result == "실패사례" and not fail_reason):
                st.error("❌ 모든 필수 항목을 입력해주세요.")
            else:
                new_data = {
                    "project": project,
                    "date": date_val.strftime("%Y-%m-%d"),
                    "work_type": work_type,
                    "result": case_result,
                    "defect_content": defect_content,
                    "details": details,
                    "solution": solution,
                    "fail_reason": fail_reason
                }
                save_to_sheet("knowledge_db", "defect_cases", new_data)
                st.success("✅ 하자사례가 저장되었습니다.")
                st.session_state.chat_history.append({"role": "assistant", "content": "✅ 하자사례가 저장되었습니다."})
                st.session_state.register_type = None
                st.session_state.autofill_result = None
                st.experimental_rerun()

    elif st.session_state.register_type == "VE사례":
        st.info("➡️ GPT가 이 입력을 **VE사례**로 분류했습니다. (VE 자동입력은 추후 지원 예정)")
