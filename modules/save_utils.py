import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import streamlit as st

# 🔐 구글 서비스 계정 인증
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_info(
    st.secrets["GCP_SERVICE_ACCOUNT"], scopes=SCOPE
)
CLIENT = gspread.authorize(CREDS)

# 📄 워크시트 접근 함수
def get_worksheet(sheet_name: str, worksheet_name: str):
    spreadsheet = CLIENT.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet

# 💾 구글 시트에 데이터 누적 저장 함수
def save_to_sheet(sheet_name: str, worksheet_name: str, new_data: dict):
    worksheet = get_worksheet(sheet_name, worksheet_name)

    # 기존 데이터 불러오기 (빈 행 제거)
    try:
        df_existing = get_as_dataframe(worksheet).dropna(how='all')
    except:
        df_existing = pd.DataFrame()

    # 새로운 데이터 추가
    new_row = pd.DataFrame([new_data])
    df_combined = pd.concat([df_existing, new_row], ignore_index=True)

    # 기존 내용 초기화 후 저장
    worksheet.clear()
    set_with_dataframe(worksheet, df_combined)
