from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ReportCustomerResponse(BaseModel):
    id: int
    customer_code: str
    name: str


class ReportPhaseResponse(BaseModel):
    phase_name: str
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None


class ReportTaskAnswerResponse(BaseModel):
    question: str
    answer: Optional[str] = None


class ReportTaskExecutionResponse(BaseModel):
    start_time: Optional[datetime] = None
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None

    completed_time: Optional[datetime] = None
    completed_latitude: Optional[float] = None
    completed_longitude: Optional[float] = None

    status: Optional[str] = None

    client_signature: Optional[str] = None
    client_photo: Optional[str] = None


class ReportTaskResponse(BaseModel):
    task_id: int
    task_number: str

    title: str

    status: str

    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None

    created_at: Optional[datetime] = None
    due_date: Optional[date] = None

    execution: Optional[
        ReportTaskExecutionResponse
    ] = None

    questions_and_answers: list[
        ReportTaskAnswerResponse
    ] = []


class ReportTicketResponse(BaseModel):
    ticket_id: int
    ticket_number: str

    ticket_type: str
    priority: str

    complaint_description: str

    status: str

    closing_remarks: Optional[str] = None

    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    

class LiftReportResponse(BaseModel):
    lift_id: int
    lift_code: str

    customer: ReportCustomerResponse

    current_phase: Optional[str] = None

    phase_history: list[
        ReportPhaseResponse
    ] = []

    tasks: list[
        ReportTaskResponse
    ] = []

    tickets: list[
        ReportTicketResponse
    ] = []

class AttendanceEmployeeResponse(BaseModel):
    employee_id: int
    employee_code: Optional[str] = None
    name: str
    department: Optional[str] = None
    designation: Optional[str] = None
    role: Optional[str] = None


class DailyAttendanceResponse(BaseModel):
    date: date
    day: str
    status: str

    present: list[AttendanceEmployeeResponse] = []
    absent: list[AttendanceEmployeeResponse] = []


class MonthlyAttendanceResponse(BaseModel):
    year: int
    month: int

    total_days: int
    total_holidays: int
    total_working_days: int
    total_present: int
    total_absent: int

    days: list[DailyAttendanceResponse] = []