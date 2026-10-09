from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DesignationBase(BaseModel):
    """
    Common designation fields.
    """

    name: str
    description: str | None = None


class DesignationCreate(DesignationBase):
    """
    Schema for creating a designation.
    """

    pass


class DesignationUpdate(BaseModel):
    """
    Schema for updating a designation.
    """

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class DesignationResponse(BaseModel):
    """
    Schema for designation response.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    designation_code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime