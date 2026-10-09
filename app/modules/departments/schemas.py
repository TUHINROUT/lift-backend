from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    """
    Request schema for creating a department.
    """

    name: str = Field(
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=255,
    )


class DepartmentUpdate(BaseModel):
    """
    Request schema for updating a department.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=255,
    )


class DepartmentResponse(BaseModel):
    """
    Response schema for department.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    department_code: str
    name: str
    description: str | None
    is_active: bool


class DepartmentListResponse(DepartmentResponse):
    """
    Response schema for listing departments.
    """

    pass