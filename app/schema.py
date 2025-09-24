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

class UserDatastorageRequest(BaseModel):
    user_id: str = Field(..., example="12345")
    user_name: str = Field(..., example="John Doe")
    user_email: str = Field(..., example="john_doe25@gmail.com")
    date_time_started: str = Field(..., example="2023-10-01 10:00:00")
    date_time_last_active: str = Field(..., example="2023-10-01 11:00:00")
    legal_category: str = Field(..., example="Conveyancing")
    location: str = Field(..., example="London")
    drop_off_stage: str = Field(..., example="Initial Contact")

    @field_validator("drop_off_stage")
    def validate_drop_off_stage(cls, value):
        valid_stages = [
            "Left before email",
            "Email provided, no brief",
            "Declined brief",
            "Brief generated, no referral",
            "Declined solicitor referral",
            "Referral sent",
        ]
        if value not in valid_stages:
            value = "Other/Unspecified"
        return value

class GetQuestionsRequest(BaseModel):
    legal_category: str = Field(..., example="Immigration")