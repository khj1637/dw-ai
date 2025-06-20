import streamlit as st
import pandas as pd
from modules.save_utils import save_to_sheet

# 🔧 하자사례 입력 폼
def render_defect_form(sheet_name, worksheet_name):
    st.subheader("하자사례 입력")
    with st.form("form_defect"):
        project = st.text_input("현장명", key="defect_project")
        date_val = st.date_input("발생일", key="defect_date")
        work_type = st.text_input("공종", key="defect_work_type")
        result = st.radio("사례 결과", ["성공사례", "실패사례"], key="defect_result")
        defect_content = st.text_input("하자 내용", key="defect_content")
        details = st.text_area("상세 내용", key="defect_details")

        solution = ""
        fail_reason = ""
        if result == "성공사례":
            solution = st.text_input("해결 방안", key="defect_solution")
        else:
            fail_reason = st.text_input("실패 원인", key="defect_fail_reason")

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
                    "date": date_val.strftime("%Y-%m-%d"),
                    "work_type": work_type,
                    "result": result,
                    "defect_content": defect_content,
                    "details": details,
                    "solution": solution,
                    "fail_reason": fail_reason
                }
                save_to_sheet(sheet_name, worksheet_name, new_data)
                st.success("✅ 하자사례가 저장되었습니다.")

                for key in [
                    "defect_project", "defect_date", "defect_work_type", "defect_result",
                    "defect_content", "defect_details", "defect_solution", "defect_fail_reason"
                ]:
                    st.session_state.pop(key, None)

# 💡 VE사례 입력 폼
def render_ve_form(sheet_name, worksheet_name):
    st.subheader("VE사례 입력")
    with st.form(key="ve_form"):
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

        submitted = st.form_submit_button("저장하기")

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
                "date": date_val.strftime("%Y-%m-%d"),
                "work_type": work_type,
                "result": result,
                "ve_content": ve_content,
                "details": details,
                "effect": effect,
                "fail_reason": fail_reason
            }
            save_to_sheet(sheet_name, worksheet_name, new_data)
            st.success("✅ VE사례가 저장되었습니다.")

            for key in [
                "ve_project", "ve_date", "ve_work_type", "ve_result",
                "ve_content", "ve_details", "ve_effect", "ve_fail_reason"
            ]:
                st.session_state.pop(key, None)

# 📅 공사기간 입력 폼
def render_duration_form(sheet_name, worksheet_name):
    st.subheader("공사기간 입력")
    with st.form(key="duration_form"):
        project = st.text_input("현장명", key="duration_project")
        usage = st.text_input("용도", key="duration_usage")
        structure = st.text_input("구조형식", key="duration_structure")
        land_area = st.number_input("대지면적 (㎡)", min_value=0.0, key="duration_land_area")
        building_area = st.number_input("건축면적 (㎡)", min_value=0.0, key="duration_building_area")
        total_floor_area = st.number_input("연면적 (㎡)", min_value=0.0, key="duration_total_floor_area")
        above_ground = st.number_input("지상층수", min_value=0, step=1, key="duration_above_ground")
        underground = st.number_input("지하층수", min_value=0, step=1, key="duration_underground")
        height = st.number_input("최고높이 (m)", min_value=0.0, key="duration_height")
        duration = st.number_input("전체 공사기간 (일)", min_value=1, step=1, key="duration_duration")

        submitted = st.form_submit_button("저장하기")

    if submitted:
        if not all([project, usage, structure]):
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

            for key in [
                "duration_project", "duration_usage", "duration_structure",
                "duration_land_area", "duration_building_area", "duration_total_floor_area",
                "duration_above_ground", "duration_underground", "duration_height", "duration_duration"
            ]:
                st.session_state.pop(key, None)

# 📁 기타사례 입력 폼
def render_etc_form(sheet_name, worksheet_name):
    st.subheader("기타사례 입력")
    with st.form(key="etc_form"):
        project = st.text_input("현장명", key="etc_project")
        date_val = st.date_input("등록일", key="etc_date")
        etc_content = st.text_input("관련 내용", key="etc_content")
        details = st.text_area("상세 내용", key="etc_details")

        submitted = st.form_submit_button("저장하기")

    if submitted:
        if not all([project, etc_content, details]):
            st.error("❌ 모든 항목을 입력해 주세요.")
        else:
            new_data = {
                "project": project,
                "date": date_val.strftime("%Y-%m-%d"),
                "etc_content": etc_content,
                "details": details
            }
            save_to_sheet(sheet_name, worksheet_name, new_data)
            st.success("✅ 기타사례가 저장되었습니다.")

            for key in ["etc_project", "etc_date", "etc_content", "etc_details"]:
                st.session_state.pop(key, None)
