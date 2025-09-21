from fastapi import APIRouter
from app.schema import OrganisationSearchRequest, EmailRequest
from app.utils.distance_calculator import DistanceCalculator
from app.utils.email_handler import EmailHandler
router = APIRouter()
distance_calculator = DistanceCalculator()
email_handler = EmailHandler()

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