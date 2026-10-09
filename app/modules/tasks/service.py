from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC
from app.modules.lifts.repository import LiftRepository
from app.modules.tasks.models import Task,TaskExecution,TaskQuestion, TaskAnswer
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
from app.modules.users.repository import UsersRepository
from app.modules.tickets.repository import TicketRepository
from app.common.enums import TicketStatus, TaskStatus
from app.modules.attendance.repository import AttendanceRepository
from app.common.utils import distance_in_meters
from app.services.email import send_email


class TaskService:
    def __init__(self, db: AsyncSession):
        self.repository = TaskRepository(db)
        self.lift_repository = LiftRepository(db)
        self.user_repository = UsersRepository(db)
        self.ticket_repository = TicketRepository(db)
        self.attendance_repository = AttendanceRepository(db)

    def _to_response(
        self,
        task: Task,
    ) -> TaskResponse:

        return TaskResponse(
            id=task.id,
            task_number=task.task_number,
            lift_id=task.lift_id,
            assigned_to=task.assigned_to,
            assigned_by=task.assigned_by,
            assigned_by_name=(
                f"{task.assigned_manager.first_name} "
                f"{task.assigned_manager.last_name}"
            ),
            category=task.category,
            sub_category=task.sub_category,
            priority=task.priority,
            ticket_id=task.ticket_id,
            due_date=task.due_date,
            latitude=float(task.latitude),
            longitude=float(task.longitude),
            allowed_radius=float(task.allowed_radius),
            location_name=task.location_name,
            instructions=task.instructions,
            attachment=task.attachment,
            status=task.status,
            is_active=task.is_active,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    async def create_task(
        self,
        task_data: TaskCreate,
        assigned_by: int,
    ) -> TaskResponse:

        existing_lift = await self.lift_repository.get_by_id(
            task_data.lift_id
        )

        if existing_lift is None:
            raise ValueError("Lift not found.")
        
        if task_data.ticket_id is not None:
            ticket = await self.ticket_repository.get_by_id(
                task_data.ticket_id
            )

            if ticket is None:
                raise ValueError("Ticket not found.")

            if ticket.status == TicketStatus.CLOSED:
                raise ValueError(
                    "Cannot assign task to a closed ticket."
                )

        employee = await self.user_repository.get_user_by_id(
            task_data.assigned_to
        )

        if employee is None:
            raise ValueError("Assigned employee not found.")

        last_task = await self.repository.get_last_task()

        if last_task is None:
            next_number = 1
        else:
            last_code = last_task.task_number
            next_number = int(last_code.replace("TASK", "")) + 1

        task_number = f"TASK{next_number:06d}"

        task = Task(
            task_number=task_number,
            lift_id=task_data.lift_id,
            assigned_to=task_data.assigned_to,
            assigned_by=assigned_by,
            category=task_data.category,
            sub_category=task_data.sub_category,
            priority=task_data.priority,
            ticket_id=task_data.ticket_id,
            due_date=task_data.due_date,
            latitude=task_data.latitude,
            longitude=task_data.longitude,
            location_name=task_data.location_name,
            allowed_radius=task_data.allowed_radius,
            instructions=task_data.instructions,
            attachment=task_data.attachment,
            status=TaskStatus.PENDING,
        )
        created_task = await self.repository.create(task)
        send_email(
                to_email=employee.email,
                subject=f"New Task Assigned - {created_task.task_number}",
                body=(
                    f"Hello {employee.first_name} {employee.last_name},\n\n"
                    f"A new task has been assigned to you.\n\n"
                    f"Task Number: {created_task.task_number}\n"
                    f"Category: {created_task.category}\n"
                    f"Sub Category: {created_task.sub_category}\n"
                    f"Priority: {created_task.priority}\n"
                    f"Due Date: {created_task.due_date}\n"
                    f"Location: {created_task.location_name}\n\n"
                    f"Please log in to the application to view the complete task details.\n\n"
                    f"Regards,\n"
                    f"Evio Elevator"
                ),
            )
        return self._to_response(created_task)

    async def get_tasks(
        self,
    ) -> list[Task]:
        task_list = await self.repository.get_all()
        return [
            self._to_response(task)
            for task in task_list
        ]

    async def get_employee_tasks(
        self,
        employee_id: int,
    ) -> list[Task]:
        
        task_list = await self.repository.get_by_employee(employee_id)

        return [
            self._to_response(task)
            for task in task_list
        ]

    async def get_task_by_id(
        self,
        task_id: int,
    ) -> Task:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        return task

    async def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
    ) -> Task:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        if task.status in [
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
        ]:
            raise ValueError(
                "In-progress or completed tasks cannot be edited."
            )

        if task_data.assigned_to is not None:

            employee = await self.user_repository.get_user_by_id(
                task_data.assigned_to
            )

            if employee is None:
                raise ValueError("Assigned employee not found.")

            task.assigned_to = task_data.assigned_to

        if task_data.category is not None:
            task.category = task_data.category

        if task_data.sub_category is not None:
            task.sub_category = task_data.sub_category

        if task_data.ticket_id is not None:
            ticket = await self.ticket_repository.get_by_id(
                task_data.ticket_id
            )

            if ticket is None:
                raise ValueError("Ticket not found.")

            if ticket.status == TicketStatus.CLOSED:
                raise ValueError(
                    "Cannot assign task to a closed ticket."
                )

            task.ticket_id = task_data.ticket_id

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.location_name is not None:
            task.location_name = task_data.location_name

        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        if task_data.latitude is not None:
            task.latitude = task_data.latitude

        if task_data.longitude is not None:
            task.longitude = task_data.longitude

        if task_data.allowed_radius is not None:
            task.allowed_radius = task_data.allowed_radius

        if task_data.instructions is not None:
            task.instructions = task_data.instructions

        if task_data.attachment is not None:
            task.attachment = task_data.attachment

        if task_data.status is not None:
            task.status = task_data.status

        return await self.repository.update(task)

    async def activate_task(
        self,
        task_id: int,
    ) -> Task:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        return await self.repository.activate(task)

    async def deactivate_task(
        self,
        task_id: int,
    ) -> Task:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        return await self.repository.deactivate(task)

    async def start_task(
        self,
        task_id: int,
        employee_id: int,
        latitude: float,
        longitude: float,
    ) -> TaskExecution:

        today = datetime.now(UTC).date()

        attendance = await self.attendance_repository.get_by_user_and_date(
            user_id=employee_id,
            attendance_date=today,
        )

        if attendance is None or attendance.punch_in_time is None:
            raise ValueError(
                "Punch In is required before starting a task."
            )

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        if not task.is_active:
            raise ValueError("Task is inactive.")

        if task.assigned_to != employee_id:
            raise ValueError(
                "This task is not assigned to you."
            )

        existing_execution = await self.repository.get_execution(
            task_id=task_id,
            employee_id=employee_id,
        )

        if existing_execution is not None:
            raise ValueError(
                "Task has already been started."
            )

        distance = distance_in_meters(
            latitude,
            longitude,
            float(task.latitude),
            float(task.longitude),
        )

        if distance > float(task.allowed_radius):
            raise ValueError(
                "You are outside the allowed task location."
            )

        now = datetime.now(UTC)

        execution = TaskExecution(
            task_id=task_id,
            employee_id=employee_id,
            start_time=now,
            start_latitude=latitude,
            start_longitude=longitude,
            status="IN_PROGRESS",
        )
        task.status = TaskStatus.IN_PROGRESS

        return await self.repository.create_execution(execution)

    async def create_question(
        self,
        task_id: int,
        question: str,
    ) -> TaskQuestion:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise ValueError("Task not found.")
        if not question.strip():
            raise ValueError("Question cannot be empty.")
        task_question = TaskQuestion(
            task_id=task_id,
            question=question.strip(),
        )
        return await self.repository.create_question(
            task_question
        )


    async def create_answer(
        self,
        task_id: int,
        employee_id: int,
        question_id: int,
        answer: str,
    ) -> TaskAnswer:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        if task.assigned_to != employee_id:
            raise ValueError(
                "This task is not assigned to you."
            )

        execution = await self.repository.get_execution(
            task_id=task_id,
            employee_id=employee_id,
        )

        if execution is None:
            raise ValueError(
                "Task must be started before submitting an answer."
            )

        if execution.status != "IN_PROGRESS":
            raise ValueError(
                "Task is not currently in progress."
            )

        questions = await self.repository.get_questions(
            task_id
        )

        question = next(
            (
                item
                for item in questions
                if item.id == question_id
            ),
            None,
        )

        if question is None:
            raise ValueError(
                "Question does not belong to this task."
            )

        if not answer.strip():
            raise ValueError(
                "Answer cannot be empty."
            )

        task_answer = TaskAnswer(
            execution_id=execution.id,
            question_id=question_id,
            answer=answer.strip(),
        )

        return await self.repository.create_answer(
            task_answer
        )


    async def get_answers(
        self,
        task_id: int,
        employee_id: int,
    ) -> list[TaskAnswer]:

        execution = await self.repository.get_execution(
            task_id=task_id,
            employee_id=employee_id,
        )

        if execution is None:
            raise ValueError(
                "Task has not been started."
            )

        return await self.repository.get_answers(
            execution_id=execution.id
        )


    async def get_questions(
        self,
        task_id: int,
    ) -> list[TaskQuestion]:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise ValueError("Task not found.")
        return await self.repository.get_questions(
            task_id
        )

    async def complete_task(
        self,
        task_id: int,
        employee_id: int,
        latitude: float,
        longitude: float,
        client_signature: str | None = None,
        client_photo: str | None = None,
    ) -> TaskExecution:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        if task.assigned_to != employee_id:
            raise ValueError(
                "This task is not assigned to you."
            )

        execution = await self.repository.get_execution(
            task_id=task_id,
            employee_id=employee_id,
        )

        if execution is None:
            raise ValueError(
                "Task must be started before completing it."
            )

        if execution.status != "IN_PROGRESS":
            raise ValueError(
                "Task is not currently in progress."
            )

        questions = await self.repository.get_questions(
            task_id
        )

        answers = await self.repository.get_answers(
            execution_id=execution.id
        )

        answered_question_ids = {
            answer.question_id
            for answer in answers
        }

        missing_questions = [
            question.id
            for question in questions
            if question.id not in answered_question_ids
        ]

        if missing_questions:
            raise ValueError(
                "Please answer all task questions before completing the task."
            )

        if (
            client_signature is None
            and client_photo is None
        ):
            raise ValueError(
                "Client signature or client photo is required."
            )

        distance = distance_in_meters(
            latitude,
            longitude,
            float(task.latitude),
            float(task.longitude),
        )

        if distance > float(task.allowed_radius):
            raise ValueError(
                "You are outside the allowed task location."
            )

        now = datetime.now(UTC)

        execution.completed_time = now
        execution.completed_latitude = latitude
        execution.completed_longitude = longitude
        execution.client_signature = client_signature
        execution.client_photo = client_photo
        execution.status = "COMPLETED"
        task.status = TaskStatus.COMPLETED
        await self.repository.update_execution(
            execution
        )
        await self.repository.update(task)

        return execution

    async def get_task_details(
        self,
        task_id: int,
    ) -> dict:

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise ValueError("Task not found.")

        execution = await self.repository.get_execution_by_task(
            task_id=task_id
        )

        questions = await self.repository.get_questions(
            task_id=task_id
        )

        question_answers = []

        if execution is not None:
            answers = await self.repository.get_answers(
                execution_id=execution.id
            )

            answer_map = {
                answer.question_id: answer.answer
                for answer in answers
            }

            for question in questions:
                question_answers.append(
                    {
                        "question_id": question.id,
                        "question": question.question,
                        "answer": answer_map.get(question.id),
                    }
                )
        else:
            for question in questions:
                question_answers.append(
                    {
                        "question_id": question.id,
                        "question": question.question,
                        "answer": None,
                    }
                )

        return {
            "task": self._to_response(task),
            "execution": execution,
            "questions": question_answers,
        }