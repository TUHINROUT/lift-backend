from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.sales_visits.models import SalesVisitStatus


class SalesVisitCreate(BaseModel):
    client_name: str = Field(..., min_length=2, max_length=200)
    contact_person: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    location: str = Field(..., min_length=2, max_length=255)

    lift_type: str = Field(..., min_length=2, max_length=200)
    units: int = Field(..., ge=1)

    estimated_quote: Decimal = Field(..., ge=0)

    visit_date: date
    visit_time: time

    status: SalesVisitStatus = SalesVisitStatus.NEW_LEAD

    notes: str | None = None
    site_image: str | None = None


class SalesVisitUpdate(BaseModel):
    client_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    contact_person: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    lift_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    units: int | None = Field(
        default=None,
        ge=1,
    )

    estimated_quote: Decimal | None = Field(
        default=None,
        ge=0,
    )

    visit_date: date | None = None
    visit_time: time | None = None

    status: SalesVisitStatus | None = None

    notes: str | None = None
    site_image: str | None = None


class SalesVisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_number: str

    created_by: int

    client_name: str
    contact_person: str
    phone: str
    location: str

    lift_type: str
    units: int
    estimated_quote: Decimal

    visit_date: date
    visit_time: time

    status: SalesVisitStatus

    notes: str | None
    site_image: str | None

    created_at: object
    updated_at: object