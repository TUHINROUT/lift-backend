from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str | None
    email: EmailStr
    first_name: str
    last_name: str
    profile_photo: str | None
    company_id: int | None
    designation_id: int | None
    department_id: int | None
    designation_name:str | None
    department_name:str | None
    is_verified: bool
    is_superuser: bool
    is_active: bool

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str