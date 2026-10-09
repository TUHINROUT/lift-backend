from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PunchInRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PunchOutRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name:str
    date: date

    punch_in_time: datetime | None
    punch_in_latitude: float | None
    punch_in_longitude: float | None

    punch_out_time: datetime | None
    punch_out_latitude: float | None
    punch_out_longitude: float | None

    working_hours: float | None
    status: str

    created_at: datetime
    updated_at: datetime

class AttendanceTrackingResponse(BaseModel):
    employee_id: int
    employee_code: str | None = None
    name: str

    department: str | None = None
    designation: str | None = None
    role: str | None = None

    date: date

    status: str

    punch_in_time: datetime | None = None
    punch_in_latitude: float | None = None
    punch_in_longitude: float | None = None

    punch_out_time: datetime | None = None
    punch_out_latitude: float | None = None
    punch_out_longitude: float | None = None

    working_hours: float | None = None

class AttendanceTrackingSummaryResponse(BaseModel):
    date: date
    total_employees: int
    present: int
    absent: int