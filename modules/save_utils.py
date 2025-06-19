import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import os

# 🔐 인증 및 워크시트 객체 가져오기
def get_worksheet(sheet_name: str, worksheet_name: str):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = os.path.join("credentials", "streamlit-knowledge-db.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet

# 💾 Google Sheet에 데이터 누적 저장
def save_to_sheet(sheet_name: str, worksheet_name: str, new_data: dict):
    worksheet = get_worksheet(sheet_name, worksheet_name)

    # 기존 데이터 불러오기
    try:
        df_existing = get_as_dataframe(worksheet).dropna(how='all')
    except:
        df_existing = pd.DataFrame()

    # 새로운 row 추가
    new_row = pd.DataFrame([new_data])
    df_combined = pd.concat([df_existing, new_row], ignore_index=True)

    # 시트 초기화 후 재작성
    worksheet.clear()
    set_with_dataframe(worksheet, df_combined)
