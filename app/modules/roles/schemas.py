from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime