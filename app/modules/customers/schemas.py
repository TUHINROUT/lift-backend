from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    """
    Common customer fields.
    """

    project_name: str
    contact_person: str | None = None
    mobile: str
    alternate_mobile: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    gst_number: str | None = None
    description: str | None = None


class CustomerCreate(CustomerBase):
    """
    Schema for creating a customer.
    """

    pass


class CustomerUpdate(BaseModel):
    """
    Schema for updating a customer.
    """

    project_name: str | None = None
    contact_person: str | None = None
    mobile: str | None = None
    alternate_mobile: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    gst_number: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    """
    Schema for customer response.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_code: str
    project_name: str
    contact_person: str | None
    mobile: str
    alternate_mobile: str | None
    email: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    gst_number: str | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime