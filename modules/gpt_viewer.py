import streamlit as st
from modules.save_utils import save_to_sheet
from modules.gpt_extract_fields import extract_defect_fields
import datetime

# 필수 항목 체크 함수
def all_required_fields_filled(state):
    required = ["project", "date_val", "work_type", "defect_content", "details", "result"]
    if not all(state.get(f) for f in required):
        return False
    if state["result"] == "성공사례":
        return bool(state.get("solution"))
    else:
        return bool(state.get("fail_reason"))

# GPT 기반 지식순환 입력 탭
def render_gpt_viewer():
    st.subheader("🧠 지식순환 GPT (정보 등록)")
    st.markdown("자연어로 하자사례를 입력하면, GPT가 자동으로 항목을 분류하고 저장을 도와줍니다.")

    # 초기화 버튼
    if st.button("초기화"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

    # API 키 입력
    api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")

    # 단계 초기화
    if "step" not in st.session_state:
        st.session_state.step = 0

    # STEP 0: 자연어 입력
    if st.session_state.step == 0:
        user_input = st.text_area("📌 하자사례를 자연어로 입력해주세요.")
        if st.button("1️⃣ GPT로 항목 추출하기") and user_input and api_key:
            with st.spinner("GPT가 항목을 분석 중입니다..."):
                result = extract_defect_fields(user_input, api_key)
                if "error" in result:
                    st.error("❌ 오류 발생: " + result["error"])
                    return
                # 결과 세션에 저장
                for key, val in result.items():
                    st.session_state[key] = val
                st.session_state.step = 1
                st.experimental_rerun()

    # STEP 1: 항목 보완 입력
    elif st.session_state.step == 1:
        st.info("🔍 부족한 정보를 확인하고 입력해주세요.")
        st.session_state.project = st.text_input("현장명", st.session_state.get("project", ""))
        st.session_state.date_val = st.date_input("발생일", value=st.session_state.get("date_val", datetime.date.today()))
        st.session_state.work_type = st.text_input("공종", st.session_state.get("work_type", ""))
        st.session_state.result = st.radio("사례 결과", ["성공사례", "실패사례"], index=0 if st.session_state.get("result") == "성공사례" else 1)
        st.session_state.defect_content = st.text_input("하자 내용", st.session_state.get("defect_content", ""))
        st.session_state.details = st.text_area("상세 내용", st.session_state.get("details", ""))

        if st.session_state.result == "성공사례":
            st.session_state.solution = st.text_input("해결 방안", st.session_state.get("solution", ""))
        else:
            st.session_state.fail_reason = st.text_input("실패 원인", st.session_state.get("fail_reason", ""))

        if all_required_fields_filled(st.session_state):
            st.success("✅ 모든 항목이 입력되었습니다.")
            if st.button("2️⃣ GPT: 지식저장소에 저장할까요?"):
                st.session_state.step = 2
                st.experimental_rerun()
        else:
            st.warning("⚠️ 아직 모든 항목이 입력되지 않았습니다.")

    # STEP 2: 사용자 승인 후 저장
    elif st.session_state.step == 2:
        st.info("📦 GPT가 제안합니다: 이 정보를 지식저장소(Google Sheets)에 저장할까요?")
        if st.button("예, 저장할게요"):
            row = {
                "현장명": st.session_state.project,
                "발생일": str(st.session_state.date_val),
                "공종": st.session_state.work_type,
                "사례 결과": st.session_state.result,
                "하자 내용": st.session_state.defect_content,
                "상세 내용": st.session_state.details,
                "해결 방안": st.session_state.solution if st.session_state.result == "성공사례" else "",
                "실패 원인": st.session_state.fail_reason if st.session_state.result == "실패사례" else ""
            }
            save_to_sheet("knowledge_db", "defect_cases", row)
            st.success("✅ 저장이 완료되었습니다!")
            st.session_state.step = 3
            st.experimental_rerun()

    # STEP 3: 완료
    elif st.session_state.step == 3:
        st.success("🎉 사례가 저장되었습니다. 새 입력을 원하시면 '초기화'를 눌러주세요.")
