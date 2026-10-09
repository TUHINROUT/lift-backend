from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.common.enums import (
    TicketPriority,
    TicketStatus,
    TicketType,
)


class TicketBase(BaseModel):
    ticket_number: str
    customer_id: int
    contact_person: str
    contact_number: str
    lift_id: int
    ticket_type: TicketType
    priority: TicketPriority
    complaint_description: str


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):

    customer_id: int | None = None
    contact_person: str | None = None
    contact_number: str | None = None
    lift_id: int | None = None
    ticket_type: TicketType | None = None
    priority: TicketPriority | None = None
    complaint_description: str | None = None

    status: TicketStatus | None = None

    closing_remarks: str | None = None

    # closed_by: int | None = None
    # closed_at: datetime | None = None

    is_active: bool | None = None


class TicketResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    ticket_number: str

    customer_id: int
    contact_person: str
    contact_number: str

    lift_id: int

    ticket_type: TicketType
    priority: TicketPriority

    complaint_description: str

    status: TicketStatus

    created_by: int

    closed_by: int | None
    closed_at: datetime | None

    closing_remarks: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime

class TicketClose(BaseModel):
    closing_remarks: str