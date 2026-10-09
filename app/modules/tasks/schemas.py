from datetime import date, datetime

from pydantic import BaseModel, ConfigDict
from app.common.enums import TaskStatus


class TaskBase(BaseModel):
    lift_id: int
    assigned_to: int
    category: str
    sub_category: str
    ticket_id: int | None = None
    priority: str
    due_date: date
    latitude: float
    longitude: float
    location_name: str
    allowed_radius: float
    instructions: str | None = None
    attachment: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    assigned_to: int | None = None
    category: str | None = None
    sub_category: str | None = None
    ticket_id: int | None = None
    priority: str | None = None
    due_date: date | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    allowed_radius: float | None = None
    instructions: str | None = None
    attachment: str | None = None
    status: TaskStatus | None = None
    is_active: bool | None = None

class TaskStartRequest(BaseModel):
    latitude: float
    longitude: float

class TaskCompleteRequest(BaseModel):
    latitude: float
    longitude: float

class TaskQuestionCreate(BaseModel):
    question: str


class TaskQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    question: str
    created_at: datetime
    updated_at: datetime

class TaskAnswerCreate(BaseModel):
    question_id: int
    answer: str


class TaskAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    execution_id: int
    question_id: int
    answer: str
    created_at: datetime
    updated_at: datetime

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_number: str

    lift_id: int

    assigned_to: int
    assigned_by: int
    assigned_by_name: str

    category: str
    sub_category: str
    priority: str
    ticket_id: int | None
    due_date: date

    latitude: float
    longitude: float
    allowed_radius: float
    location_name: str

    instructions: str | None
    attachment: str | None

    status: TaskStatus | None = None

    is_active: bool
    created_at: datetime
    updated_at: datetime

class TaskExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    employee_id: int

    start_time: datetime | None
    start_latitude: float | None
    start_longitude: float | None

    completed_time: datetime | None
    completed_latitude: float | None
    completed_longitude: float | None

    status: TaskStatus | None = None

    client_signature: str | None
    client_photo: str | None


class TaskQuestionAnswerResponse(BaseModel):
    question_id: int
    question: str
    answer: str | None


class TaskDetailsResponse(BaseModel):
    task: TaskResponse
    execution: TaskExecutionResponse | None
    questions: list[TaskQuestionAnswerResponse]