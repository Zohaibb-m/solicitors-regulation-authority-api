from fastapi import APIRouter
from app.schema import OrganisationSearchRequest, EmailRequest, GeneratePDFRequest
from app.utils.organization_data_maker import OrganizationDataMaker
from app.utils.distance_calculator import DistanceCalculator
from app.utils.email_handler import EmailHandler
from app.utils.pdf_saver import PDFSaver
from apscheduler.schedulers.background import BackgroundScheduler

router = APIRouter()
distance_calculator = DistanceCalculator()
data_maker = OrganizationDataMaker()
email_handler = EmailHandler()
pdf_saver = PDFSaver()
scheduler = BackgroundScheduler()

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
    email_handler.send_email(request.client_name, request.firm_name, request.location, request.contact, request.legal_matter_type, request.email_to, request.pdf_url, request.user_type)
    return {"message": "This endpoint will handle sending briefs via email."}

@router.post("/generate-pdf")
def generate_pdf(request: GeneratePDFRequest):
    pdf_url = pdf_saver.upload_to_blob(request.text, request.client_name)
    return {"pdf_url": pdf_url}