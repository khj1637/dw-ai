import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd

# ✅ gspread 클라이언트 생성
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["GCP_SERVICE_ACCOUNT"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

# ✅ 시트 객체 가져오기
def get_worksheet(sheet_name: str, worksheet_name: str):
    client = get_gspread_client()
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet

# ✅ 데이터 누적 저장 함수
def save_to_sheet(sheet_name: str, worksheet_name: str, new_data: dict):
    worksheet = get_worksheet(sheet_name, worksheet_name)

    try:
        existing = worksheet.get_all_records()
        df_existing = pd.DataFrame(existing)
    except Exception:
        df_existing = pd.DataFrame()

    new_row = pd.DataFrame([new_data])
    df_combined = pd.concat([df_existing, new_row], ignore_index=True)

    # 시트 전체 초기화 후 업데이트
    worksheet.clear()
    worksheet.update([df_combined.columns.values.tolist()] + df_combined.values.tolist())