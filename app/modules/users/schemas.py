from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """
    Schema for creating a user.
    """

    first_name: str
    last_name: str
    email: EmailStr
    password: str

    employee_code: str | None = None
    company_id: int | None = None
    department_id: int | None = None
    designation_id: int | None = None
    role_id: int | None = None

    profile_photo: str | None = None


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    """

    first_name: str | None = None
    last_name: str | None = None

    employee_code: str | None = None
    company_id: int | None = None
    department_id: int | None = None
    designation_id: int | None = None
    role_id: int | None = None

    profile_photo: str | None = None

    is_active: bool | None = None
    is_verified: bool | None = None
    is_superuser: bool | None = None


class UserResponse(BaseModel):
    """
    User response schema.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    employee_code: str | None

    first_name: str
    last_name: str
    email: EmailStr

    company_id: int | None
    department_id: int | None
    department_name: str | None

    designation_id: int | None
    designation_name: str | None

    role_id: int | None
    role_name: str | None

    profile_photo: str | None

    is_active: bool
    is_verified: bool
    is_superuser: bool

    last_login: datetime | None

    created_at: datetime
    updated_at: datetime