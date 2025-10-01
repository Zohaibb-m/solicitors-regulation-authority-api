import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from app.utils.helper_functions import return_response

load_dotenv()
BB_CREDENTIALS = json.loads(os.getenv("BB_CREDENTIALS"))

class GoogleSheetHandler:
    def __init__(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(BB_CREDENTIALS, scope)
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
        try:
            self.user_data_sheet.append_row(row)
            return return_response({"response": f"User: {data.user_name} added to the user data sheet."})
        except Exception as e:
            return return_response({"error": f"An error occured while trying to add data to sheet: {e}"}, error=True)

    def get_question_set(self, legal_category: str):
        try:
            return return_response({"questions": self.questionnaire_sheet.worksheet(legal_category).get_all_records()})
        except Exception as e:
            return return_response({"error": f"An error occured while retrieving questions from the sheet: {e}"}, error=True)
