import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import json

# 📌 인증 및 클라이언트 생성
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    return client

# 💾 Google Sheets에 데이터 누적 저장
def save_to_sheet(sheet_name, worksheet_name, data: dict):
    try:
        client = get_gspread_client()
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(worksheet_name)

        # 기존 데이터 불러오기
        existing = worksheet.get_all_records()
        df = pd.DataFrame(existing)

        # 새 데이터 추가
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)

        # 시트 초기화 후 저장
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    except Exception as e:
        st.error("❌ Google Sheets 저장 중 오류 발생")
        st.exception(e)
