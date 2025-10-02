import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
from app.utils.helper_functions import return_response

load_dotenv()

class DatabaseHandler():
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = create_client(url, key)
        self.payment_table = self.supabase.table("stripe_payments")

    def add_payment_record(self, email: str, name: str, payment_id: str, payment_status: str):
        response = (
            self.payment_table.insert(
                {
                    "user_email": email, 
                    "status": payment_status,
                    "user_name": name,
                    "payment_id": payment_id
                }
            ).execute()
        )

    def search_payment_status(self, email):
        try:
            one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
            response = (
                self.payment_table.select("*").eq("user_email", email)
                .gte("created_at", one_hour_ago)
                .execute()
            )
            print(response.data)
            return return_response({"payment_status": response.data[0]["status"] == "paid"})
        except Exception as e:
            return return_response({"error": f"An error occurred while searching for payment status: {e}"}, error=True)

