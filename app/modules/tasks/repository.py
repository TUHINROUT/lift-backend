from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.tasks.models import Task, TaskExecution, TaskQuestion, TaskAnswer


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_task_number(
        self,
        task_number: str,
    ) -> Task | None:
        stmt = select(Task).where(
            Task.task_number == task_number
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_last_task(
        self,
    ) -> Task | None:
        stmt = (
            select(Task)
            .order_by(Task.id.desc())
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Create task
    async def create(
        self,
        task: Task,
    ) -> Task:
        self.db.add(task)

        await self.db.flush()

        task_id = task.id

        await self.db.commit()

        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
                selectinload(Task.ticket),
            )
            .where(Task.id == task_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()

    # Get all active tasks
    async def get_all(
        self,
    ) -> list[Task]:
        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
                selectinload(Task.ticket),
            )
            .where(Task.is_active == True)
            .order_by(Task.task_number)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_employee(
        self,
        employee_id: int,
    ) -> list[Task]:
        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
                selectinload(Task.ticket),
            )
            .where(
                Task.assigned_to == employee_id,
                Task.is_active == True,
            )
            .order_by(Task.task_number)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # Get task by ID
    async def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:
        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
                selectinload(Task.ticket),
            )
            .where(Task.id == task_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_execution(
        self,
        task_id: int,
        employee_id: int,
    ) -> TaskExecution | None:

        stmt = (
            select(TaskExecution)
            .where(
                TaskExecution.task_id == task_id,
                TaskExecution.employee_id == employee_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_execution(
        self,
        execution: TaskExecution,
    ) -> TaskExecution:
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def update_execution(
        self,
        execution: TaskExecution,
    ) -> TaskExecution: 
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def create_question(
        self,
        question: TaskQuestion,
    ) -> TaskQuestion:
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question


    async def get_questions(
        self,
        task_id: int,
    ) -> list[TaskQuestion]:

        stmt = (
            select(TaskQuestion)
            .where(
                TaskQuestion.task_id == task_id
            )
            .order_by(TaskQuestion.id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_answer(
        self,
        answer: TaskAnswer,
    ) -> TaskAnswer:
        self.db.add(answer)
        await self.db.commit()
        await self.db.refresh(answer)
        return answer


    async def get_answers(
        self,
        execution_id: int,
    ) -> list[TaskAnswer]:
        stmt = (
            select(TaskAnswer)
            .where(
                TaskAnswer.execution_id == execution_id
            )
            .order_by(TaskAnswer.id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # Update task
    async def update(
        self,
        task: Task,
    ) -> Task:
        await self.db.commit()

        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
                selectinload(Task.ticket),
            )
            .where(Task.id == task.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # Activate task
    async def activate(
        self,
        task: Task,
    ) -> Task:
        task.is_active = True

        await self.db.commit()

        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
            )
            .where(Task.id == task.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # Deactivate task
    async def deactivate(
        self,
        task: Task,
    ) -> Task:
        task.is_active = False

        await self.db.commit()

        stmt = (
            select(Task)
            .options(
                selectinload(Task.lift),
                selectinload(Task.assigned_employee),
                selectinload(Task.assigned_manager),
                selectinload(Task.ticket),
            )
            .where(Task.id == task.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_execution_by_task(
        self,
        task_id: int,
    ) -> TaskExecution | None:
        stmt = (
            select(TaskExecution)
            .where(
                TaskExecution.task_id == task_id
            )
            .order_by(TaskExecution.id.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()