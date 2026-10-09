from datetime import datetime

from pydantic import BaseModel, Field


class EmployeeTrackingCreate(BaseModel):
    client_record_id: str = Field(..., min_length=1, max_length=36)
    recorded_at: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    battery_percentage: int = Field(..., ge=0, le=100)


class EmployeeTrackingBatchCreate(BaseModel):
    records: list[EmployeeTrackingCreate]

class EmployeeTrackingResponse(BaseModel):
    id: int
    client_record_id: str
    employee_id: int
    employee_name: str
    attendance_id: int
    recorded_at: datetime
    latitude: float
    longitude: float
    battery_percentage: int