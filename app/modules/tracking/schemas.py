from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class LocationPingRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    status: Optional[str] = "On Route"
    current_destination: Optional[str] = None
    battery_level: Optional[int] = 100


class EmployeeLiveLocationResponse(BaseModel):
    user_id: int
    employee_code: Optional[str] = None
    name: str
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    speed: float
    heading: float
    status: str
    current_destination: Optional[str] = None
    battery_level: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)