from datetime import date, datetime
from typing import Optional, Union
from pydantic import BaseModel, Field


class ServiceReportCreate(BaseModel):
    sl_no: Optional[str] = None
    report_date: Optional[Union[date, str]] = None

    customer_name: str
    address: str
    call_status: str = "AMC"
    instruction_from: Optional[str] = None

    problem_report: Optional[str] = None
    make: Optional[str] = "Jaguar Elevators Pvt Ltd"
    call_report_by: Optional[str] = None
    call_report_date: Optional[Union[date, str]] = None
    call_report_time: Optional[str] = None

    engineers_remarks: Optional[str] = None
    status_after_service: Optional[str] = "Complete"
    defects_found: Optional[str] = None

    start_of_service: Optional[str] = None
    end_of_service: Optional[str] = None

    rating: Optional[str] = "Satisfied"
    customer_remarks: Optional[str] = None
    customer_contact_name: Optional[str] = None
    customer_designation: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    feedback_date: Optional[Union[date, str]] = None
    place: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    engineer_signature: Optional[str] = None
    customer_signature: Optional[str] = None

    class Config:
        extra = "ignore"


class ServiceReportResponse(BaseModel):
    id: int
    sl_no: Optional[str] = None
    report_date: Optional[Union[date, str]] = None
    customer_name: str
    address: str
    call_status: Optional[str] = None
    instruction_from: Optional[str] = None
    problem_report: Optional[str] = None
    make: Optional[str] = None
    call_report_time: Optional[str] = None
    engineers_remarks: Optional[str] = None
    status_after_service: Optional[str] = None
    defects_found: Optional[str] = None
    start_of_service: Optional[str] = None
    end_of_service: Optional[str] = None
    rating: Optional[str] = None
    customer_remarks: Optional[str] = None
    customer_contact_name: Optional[str] = None
    customer_designation: Optional[str] = None
    customer_phone: Optional[str] = None
    place: Optional[str] = None
    engineer_signature: Optional[str] = None
    customer_signature: Optional[str] = None
    technician_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        extra = "ignore"