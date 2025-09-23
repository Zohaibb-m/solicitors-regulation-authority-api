from pydantic import BaseModel, Field, field_validator
from typing import Union

class OrganisationSearchRequest(BaseModel):
    post_code: str = Field(..., example="GU7 2DZ")

class EmailRequest(BaseModel):
    client_name: str = Field(..., example="Zohaib Munir")
    firm_name: list[str] = Field(..., example=["Example Firm"])
    location: str = Field(..., example="London")
    contact: str = Field(..., example="+447123456789")
    legal_matter_type: str = Field(..., example="Conveyancing")
    email_to: Union[str, list[str]] = Field(..., example=["zohaibmunir32@gmail.com"])
    pdf_url: str = Field(..., example="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
    user_type: str = Field(..., example="firms")

    @field_validator("user_type")
    def validate_user_type(cls, value):
        if value not in ["client", "firms"]:
            raise ValueError("user_type must be either 'user' or 'firm'")
        return value

class GeneratePDFRequest(BaseModel):
    text: str = Field(..., example="This is a sample text for PDF generation.\nIt supports multiple lines.")
    client_name: str = Field(..., example="Zohaib Munir")