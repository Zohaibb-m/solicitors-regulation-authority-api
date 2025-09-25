from fastapi import APIRouter
from app.schema import OrganisationSearchRequest, EmailRequest, UserDatastorageRequest, GetQuestionsRequest
from app.utils.organization_data_maker import OrganizationDataMaker
from app.utils.distance_calculator import DistanceCalculator
from app.utils.email_handler import EmailHandler
from app.utils.pdf_saver import PDFSaver
from app.utils.google_sheet_handler import GoogleSheetHandler
from apscheduler.schedulers.background import BackgroundScheduler
import json

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
    closest_organizations = distance_calculator.get_5_closest_organizations(user_postcode)
    if closest_organizations is not None:
        return closest_organizations
    else:
        return {"message": "Could not determine coordinates for the provided postcode or address."}
    
@router.post("/send-brief")
def send_brief(request: EmailRequest):
    if request.fake:
        return {"response": "Email has been sent."}
    return email_handler.send_email(request.client_name, request.firm_name, request.location, request.contact, request.legal_matter_type, request.email_to, request.pdf_url, request.user_type)

@router.post("/generate-pdf")
def generate_pdf(request: str):
    request_body = json.loads(json.loads(request))
    pdf_url = pdf_saver.upload_to_blob(request_body["text"].replace('–', '-'), request_body["client_name"])
    return {"pdf_url": pdf_url}

@router.post("/store-user-data")
def store_user_data(request: UserDatastorageRequest):
    if google_sheet_handler.store_user_data(request):
        return {"message": "User data stored successfully."}

@router.post("/get-questions")
def get_questions(request: GetQuestionsRequest):
    questions = google_sheet_handler.get_question_set(request.legal_category)
    return {"questions": questions}