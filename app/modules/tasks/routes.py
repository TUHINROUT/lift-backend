from fastapi import APIRouter,Depends,File, Form, HTTPException, UploadFile,status  
from sqlalchemy.ext.asyncio import AsyncSession
from app.storage.upload import save_file
from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TaskStartRequest,
    TaskQuestionCreate,
    TaskQuestionResponse,
    TaskAnswerCreate,
    TaskAnswerResponse,
    TaskDetailsResponse,
)
from app.modules.tasks.service import TaskService
from app.modules.users.models import User
from datetime import date

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


#! Create Task
@router.post(   
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    lift_id: int = Form(...),
    assigned_to: int = Form(...),
    category: str = Form(...),
    sub_category: str = Form(...),
    priority: str = Form(...),
    due_date: date = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: str = Form(...),
    allowed_radius: float = Form(...),
    instructions: str | None = Form(None),
    ticket_id: int | None = Form(None),
    attachment: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)

    attachment_path = None

    if attachment is not None:
        attachment_path = await save_file(
            attachment,
            "tasks",
        )

    request = TaskCreate(
        lift_id=lift_id,
        assigned_to=assigned_to,
        category=category,
        sub_category=sub_category,
        priority=priority,
        due_date=due_date,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        allowed_radius=allowed_radius,
        instructions=instructions,
        ticket_id=ticket_id,
        attachment=attachment_path,
    )

    try:
        task = await service.create_task(
            request,
            assigned_by=current_user.id,
        )
        return task

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Get All Tasks
@router.get(
    "",
    response_model=list[TaskResponse],
)
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)
    return await service.get_tasks()

@router.get(
    "/my",
    response_model=list[TaskResponse],
)
async def get_my_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = TaskService(db)

    return await service.get_employee_tasks(
        employee_id=current_user.id,
    )


#! Get Task By ID
@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)

    try:
        return await service.get_task_by_id(task_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Update Task
@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: int,
    request: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)

    try:
        return await service.update_task(
            task_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Activate Task
@router.patch(
    "/{task_id}/activate",
    response_model=TaskResponse,
)
async def activate_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)

    try:
        return await service.activate_task(task_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Deactivate Task
@router.patch(
    "/{task_id}/deactivate",
    response_model=TaskResponse,
)
async def deactivate_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)

    try:
        return await service.deactivate_task(task_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.post(
    "/{task_id}/start",
)
async def start_task(
    task_id: int,
    request: TaskStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = TaskService(db)

    try:
        return await service.start_task(
            task_id=task_id,
            employee_id=current_user.id,
            latitude=request.latitude,
            longitude=request.longitude,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.post(
    "/{task_id}/questions",
    response_model=TaskQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_question(
    task_id: int,
    request: TaskQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TaskService(db)

    try:
        return await service.create_question(
            task_id=task_id,
            question=request.question,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
@router.get(
    "/{task_id}/questions",
    response_model=list[TaskQuestionResponse],
)
async def get_task_questions(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER", "EMPLOYEE")
    ),
):
    service = TaskService(db)

    try:
        return await service.get_questions(
            task_id=task_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.post(
    "/{task_id}/answers",
    response_model=TaskAnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_answer(
    task_id: int,
    request: TaskAnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = TaskService(db)

    try:
        return await service.create_answer(
            task_id=task_id,
            employee_id=current_user.id,
            question_id=request.question_id,
            answer=request.answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
@router.get(
    "/{task_id}/answers",
    response_model=list[TaskAnswerResponse],
)
async def get_task_answers(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = TaskService(db)

    try:
        return await service.get_answers(
            task_id=task_id,
            employee_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.post(
    "/{task_id}/complete",
)
async def complete_task(
    task_id: int,
    latitude: float = Form(...),
    longitude: float = Form(...),
    client_signature: UploadFile | None = File(None),
    client_photo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = TaskService(db)

    signature_path = None
    photo_path = None

    if client_signature is not None:
        signature_path = await save_file(
            client_signature,
            "task_signatures",
        )

    if client_photo is not None:
        photo_path = await save_file(
            client_photo,
            "task_photos",
        )

    try:
        execution = await service.complete_task(
            task_id=task_id,
            employee_id=current_user.id,
            latitude=latitude,
            longitude=longitude,
            client_signature=signature_path,
            client_photo=photo_path,
        )

        return {
            "message": "Task completed successfully.",
            "execution_id": execution.id,
            "task_id": execution.task_id,
            "employee_id": execution.employee_id,
            "status": execution.status,
            "completed_time": execution.completed_time,
            "completed_latitude": execution.completed_latitude,
            "completed_longitude": execution.completed_longitude,
            "client_signature": execution.client_signature,
            "client_photo": execution.client_photo,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.get(
    "/{task_id}/details",
    response_model=TaskDetailsResponse,
)
async def get_task_details(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER", "EMPLOYEE")
    ),
):
    service = TaskService(db)
    try:
        return await service.get_task_details(
            task_id=task_id,
        )
    except ValueError as exc: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

