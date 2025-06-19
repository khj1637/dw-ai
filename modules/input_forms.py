import streamlit as st
from modules.save_utils import save_to_sheet

# 🔧 하자사례 입력 폼
def render_defect_form(sheet_name, worksheet_name):
    st.subheader("하자사례 입력")
    with st.form("form_defect"):
        project = st.text_input("현장명")
        date_val = st.date_input("발생일")
        work_type = st.text_input("공종")
        result = st.radio("사례 결과", ["성공사례", "실패사례"])
        defect_content = st.text_input("하자 내용")
        details = st.text_area("상세 내용")

        solution = ""
        fail_reason = ""
        if result == "성공사례":
            solution = st.text_input("해결 방안")
        else:
            fail_reason = st.text_input("실패 원인")

        submitted = st.form_submit_button("저장하기")
        if submitted:
            if not all([project, work_type, defect_content, details]):
                st.error("❌ 모든 항목을 입력해 주세요.")
            elif result == "성공사례" and not solution:
                st.error("❌ '해결 방안'을 입력해 주세요.")
            elif result == "실패사례" and not fail_reason:
                st.error("❌ '실패 원인'을 입력해 주세요.")
            else:
                new_data = {
                    "project": project,
                    "date": date_val,
                    "work_type": work_type,
                    "result": result,
                    "defect_content": defect_content,
                    "details": details,
                    "solution": solution,
                    "fail_reason": fail_reason
                }
                save_to_sheet(sheet_name, worksheet_name, new_data)
                st.success("✅ 하자사례가 저장되었습니다.")

# 💡 VE사례 입력 폼
def render_ve_form(sheet_name, worksheet_name):
    st.subheader("VE사례 입력")
    with st.form("form_ve"):
        project = st.text_input("현장명", key="ve_project")
        date_val = st.date_input("적용일", key="ve_date")
        work_type = st.text_input("공종", key="ve_work_type")
        result = st.radio("사례 결과", ["성공사례", "실패사례"], key="ve_result")
        ve_content = st.text_input("VE 내용", key="ve_content")
        details = st.text_area("상세 내용", key="ve_details")

        effect = ""
        fail_reason = ""
        if result == "성공사례":
            effect = st.text_input("절감 효과 / 주요 개선점", key="ve_effect")
        else:
            fail_reason = st.text_input("실패 원인", key="ve_fail_reason")

        submitted = st.form_submit_button("저장하기", key="ve_submit")
        if submitted:
            if not all([project, work_type, ve_content, details]):
                st.error("❌ 모든 항목을 입력해 주세요.")
            elif result == "성공사례" and not effect:
                st.error("❌ '절감 효과 / 개선점'을 입력해 주세요.")
            elif result == "실패사례" and not fail_reason:
                st.error("❌ '실패 원인'을 입력해 주세요.")
            else:
                new_data = {
                    "project": project,
                    "date": date_val,
                    "work_type": work_type,
                    "result": result,
                    "ve_content": ve_content,
                    "details": details,
                    "effect": effect,
                    "fail_reason": fail_reason
                }
                save_to_sheet(sheet_name, worksheet_name, new_data)
                st.success("✅ VE사례가 저장되었습니다.")

# 📅 공사기간 입력 폼
def render_duration_form(sheet_name, worksheet_name):
    st.subheader("공사기간 입력")
    with st.form("form_duration"):
        project = st.text_input("현장명", key="duration_project")
        usage = st.text_input("용도", key="duration_usage")
        structure = st.text_input("구조형식", key="duration_structure")
        land_area = st.number_input("대지면적 (㎡)", min_value=0.0, key="land_area")
        building_area = st.number_input("건축면적 (㎡)", min_value=0.0, key="building_area")
        total_floor_area = st.number_input("연면적 (㎡)", min_value=0.0, key="total_area")
        above_ground = st.number_input("지상층수", min_value=0, step=1, key="above_ground")
        underground = st.number_input("지하층수", min_value=0, step=1, key="underground")
        height = st.number_input("최고높이 (m)", min_value=0.0, key="height")
        duration = st.number_input("전체 공사기간 (일)", min_value=0, step=1, key="duration")

        submitted = st.form_submit_button("저장하기", key="duration_submit")
        if submitted:
            if not all([project, usage, structure]) or duration == 0:
                st.error("❌ 필수 항목을 모두 입력해 주세요.")
            else:
                new_data = {
                    "project": project,
                    "usage": usage,
                    "structure": structure,
                    "land_area": land_area,
                    "building_area": building_area,
                    "total_floor_area": total_floor_area,
                    "above_ground": above_ground,
                    "underground": underground,
                    "height": height,
                    "duration": duration
                }
                save_to_sheet(sheet_name, worksheet_name, new_data)
                st.success("✅ 공사기간 데이터가 저장되었습니다.")

# 📁 기타사례 입력 폼
def render_etc_form(sheet_name, worksheet_name):
    st.subheader("기타사례 입력")
    with st.form("form_etc"):
        project = st.text_input("현장명", key="etc_project")
        date_val = st.date_input("등록일", key="etc_date")
        etc_content = st.text_input("관련 내용", key="etc_content")
        details = st.text_area("상세 내용", key="etc_details")

        submitted = st.form_submit_button("저장하기", key="etc_submit")
        if submitted:
            if not all([project, etc_content, details]):
                st.error("❌ 모든 항목을 입력해 주세요.")
            else:
                new_data = {
                    "project": project,
                    "date": date_val,
                    "etc_content": etc_content,
                    "details": details
                }
                save_to_sheet(sheet_name, worksheet_name, new_data)
                st.success("✅ 기타사례가 저장되었습니다.")