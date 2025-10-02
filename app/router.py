from fastapi import APIRouter, Request, HTTPException
from flask import redirect, request
from app.schema import OrganisationSearchRequest, EmailRequest, UserDatastorageRequest, GetQuestionsRequest, CheckoutSessionRequest
from app.utils.organization_data_maker import OrganizationDataMaker
from app.utils.distance_calculator import DistanceCalculator
from app.utils.email_handler import EmailHandler
from app.utils.pdf_saver import PDFSaver
from app.utils.google_sheet_handler import GoogleSheetHandler
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.database_handler import DatabaseHandler
from app.utils.helper_functions import return_response
import json
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
distance_calculator = DistanceCalculator()
data_maker = OrganizationDataMaker()
email_handler = EmailHandler()
pdf_saver = PDFSaver()
scheduler = BackgroundScheduler()
google_sheet_handler = GoogleSheetHandler()
database_handler = DatabaseHandler()
stripe.api_key = os.getenv("STRIPE_API_KEY")

scheduler.add_job(func=data_maker.process_organization_data, trigger="interval", hours=24)
scheduler.start()

def create_data_every_24_hours():
    data_maker.process_organization_data()
    distance_calculator.read_organization_data()


@router.post("/law-firm-search")
def law_firm_search(request: OrganisationSearchRequest):
    user_postcode = request.post_code 
    return distance_calculator.get_5_closest_organizations(user_postcode)
    
@router.post("/send-brief")
def send_brief(request: EmailRequest):
    if request.fake:
        return return_response({"response": "Email has been sent."})
    return email_handler.send_email(request.client_name, request.firm_name, request.location, request.contact, request.legal_matter_type, request.email_to, request.pdf_url, request.user_type)

@router.post("/generate-pdf")
def generate_pdf(request: str):
    try: 
        request_body = json.loads(json.loads(request))
        return pdf_saver.upload_to_blob(request_body["text"].replace('–', '-'), request_body["client_name"])
    except Exception as e:
        return return_response({"error": f"An error occured while parsing json: {e}"}, error=True)
    

@router.post("/store-user-data")
def store_user_data(request: UserDatastorageRequest):
    return google_sheet_handler.store_user_data(request)

@router.post("/get-questions")
def get_questions(request: GetQuestionsRequest):
    return google_sheet_handler.get_question_set(request.legal_category)


@router.post('/create-checkout-session')
def create_checkout_session(data: CheckoutSessionRequest):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': os.getenv("PRICE_ID"),
                    'quantity': 1,
                },
            ],
            customer_email=data.email,
            mode='payment',
            invoice_creation={
                "enabled": True
            },
            success_url="http://www.google.com"
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return return_response({"error": f"The checkout session couldn't be created due to: {e}"})


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")  # from Stripe dashboard
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # Handle successful payment event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.customer_details.email
        customer_name = session.customer_details.name
        payment_id = session.id
        payment_status = session.payment_status
        database_handler.add_payment_record(customer_email, customer_name, payment_id, payment_status)

@router.post("/check_payment_status")
def check_payment_status(data: CheckoutSessionRequest):
    return database_handler.search_payment_status(data.email)
