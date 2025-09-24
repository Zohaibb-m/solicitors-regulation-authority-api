import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class GoogleSheetHandler:
    def __init__(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("BBcredentials.json", scope)
        client = gspread.authorize(creds)
        self.user_data_sheet = client.open("User database").sheet1
        self.questionnaire_sheet = client.open("Questions")

    def store_user_data(self, data: dict):
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.user_id,
            data.user_name,
            data.user_email,
            data.date_time_started,
            data.date_time_last_active,
            data.legal_category,
            data.location,
            data.drop_off_stage,
        ]
        self.user_data_sheet.append_row(row)
        return True

    def get_question_set(self, legal_category: str):
        return self.questionnaire_sheet.worksheet(legal_category).get_all_records()
