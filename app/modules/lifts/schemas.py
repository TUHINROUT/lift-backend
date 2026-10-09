from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class LiftBase(BaseModel):
    lift_code: str
    customer_id: int
    building_name: str
    address: str
    latitude: float
    longitude: float
    installation_date: date | None = None
    warranty: str | None = None
    amc: str | None = None
    status: str | None = None
    capacity: str | None = None
    lift_type: str | None = None
    machine_type: str | None = None
    controller_type: str | None = None
    door_type: str | None = None
    stops: int | None = None
    floors: int | None = None
    manufacturer: str | None = None
    serial_number: str | None = None
    drawing: str | None = None
    remarks: str | None = None


class LiftCreate(LiftBase):

    pass


class LiftUpdate(BaseModel):

    building_name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    installation_date: date | None = None
    warranty: str | None = None
    amc: str | None = None
    status: str | None = None
    capacity: str | None = None
    lift_type: str | None = None
    machine_type: str | None = None
    controller_type: str | None = None
    door_type: str | None = None
    stops: int | None = None
    floors: int | None = None
    manufacturer: str | None = None
    serial_number: str | None = None
    drawing: str | None = None
    remarks: str | None = None
    is_active: bool | None = None


class LiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lift_code: str

    customer_id: int
    customer_code: str
    project_name: str

    building_name: str
    address: str
    latitude: float
    longitude: float

    installation_date: date | None

    warranty: str | None
    amc: str | None
    status: str | None

    capacity: str | None
    lift_type: str | None
    machine_type: str | None
    controller_type: str | None
    door_type: str | None

    stops: int | None
    floors: int | None

    manufacturer: str | None
    serial_number: str | None

    drawing: str | None
    remarks: str | None

    is_active: bool
    created_at: datetime
    updated_at: datetime