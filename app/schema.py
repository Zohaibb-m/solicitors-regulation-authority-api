from pydantic import BaseModel, Field

class OrganisationSearchRequest(BaseModel):
    post_code: str = Field(..., example="GU7 2DZ")
    address: str = Field(None, example="10 Downing St, Westminster, London")

