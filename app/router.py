from fastapi import APIRouter
from flask import Flask, redirect, request
from app.schema import OrganisationSearchRequest, EmailRequest, UserDatastorageRequest, GetQuestionsRequest
from app.utils.organization_data_maker import OrganizationDataMaker
from app.utils.distance_calculator import DistanceCalculator
from app.utils.email_handler import EmailHandler
from app.utils.pdf_saver import PDFSaver
from app.utils.google_sheet_handler import GoogleSheetHandler
from apscheduler.schedulers.background import BackgroundScheduler
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
    request_body = json.loads(json.loads(request))
    return pdf_saver.upload_to_blob(request_body["text"].replace('–', '-'), request_body["client_name"])
    

@router.post("/store-user-data")
def store_user_data(request: UserDatastorageRequest):
    return google_sheet_handler.store_user_data(request)

@router.post("/get-questions")
def get_questions(request: GetQuestionsRequest):
    return google_sheet_handler.get_question_set(request.legal_category)

stripe.api_key = os.getenv("STRIPE_API_KEY")
price_id = os.getenv("PRICE_ID")
@router.post('/create-checkout-session')
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, price_1234) of the product you want to sell
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url= "http://www.google.com",
            cancel_url= "http://www.google.com",
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)