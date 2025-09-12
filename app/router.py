from fastapi import APIRouter
from app.schema import OrganisationSearchRequest
from app.utils.distance_calculator import DistanceCalculator

router = APIRouter()
distance_calculator = DistanceCalculator()

@router.post("/law-firm-search")
def law_firm_search(request: OrganisationSearchRequest):
    user_postcode = request.post_code 
    closest_organizations = distance_calculator.get_5_closest_organizations(user_postcode)
    if closest_organizations is not None:
        return closest_organizations
    else:
        return {"message": "Could not determine coordinates for the provided postcode or address."}