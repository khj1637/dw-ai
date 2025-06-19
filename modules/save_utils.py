import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 구글 서비스 계정 인증
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file(
    "streamlit-knowledge-db-4c6b135fda08.json", scopes=SCOPE
)
CLIENT = gspread.authorize(CREDS)

# 데이터 저장 함수
def save_to_sheet(sheet_name, worksheet_name, data: dict):
    try:
        sheet = CLIENT.open(sheet_name)
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
        print("[ERROR] 구글 시트 저장 오류:", e)
        raise
