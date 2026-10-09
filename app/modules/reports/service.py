import calendar
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import (
    LiftReportResponse,
    ReportCustomerResponse,
    ReportPhaseResponse,
    ReportTaskAnswerResponse,
    ReportTaskExecutionResponse,
    ReportTaskResponse,
    ReportTicketResponse,
    AttendanceEmployeeResponse,
    DailyAttendanceResponse,
    MonthlyAttendanceResponse,
)


class ReportService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repository = ReportRepository(db)


    async def get_monthly_attendance_report(
        self,
        year: int,
        month: int,
        status: str | None = None,
    ) -> MonthlyAttendanceResponse:

        if month < 1 or month > 12:
            raise ValueError(
                "Month must be between 1 and 12."
            )

        if status is not None:
            status = status.upper()
            if status not in {"PRESENT", "ABSENT"}:
                raise ValueError(
                    "Status must be PRESENT or ABSENT."
                )

        total_days = calendar.monthrange(
            year,
            month,
        )[1]

        start_date = date(
            year,
            month,
            1,
        )

        end_date = date(
            year,
            month,
            total_days,
        )

        # ---------------------------------
        # Get Active Users
        # ---------------------------------
        users = (
            await self.repository
            .get_active_users_for_attendance_report()
        )

        # ---------------------------------
        # Get Attendance For Whole Month
        # ---------------------------------
        attendance_records = (
            await self.repository
            .get_attendance_by_date_range(
                start_date=start_date,
                end_date=end_date,
            )
        )

        # ---------------------------------
        # Create Attendance Lookup
        # ---------------------------------
        attendance_by_date_and_user = {
            (
                attendance.date,
                attendance.user_id,
            ): attendance
            for attendance in attendance_records
        }

        daily_reports = []
        total_holidays = 0
        total_present = 0
        total_absent = 0

        # ---------------------------------
        # Process Every Calendar Day
        # ---------------------------------
        for day_number in range(
            1,
            total_days + 1,
        ):

            current_date = date(
                year,
                month,
                day_number,
            )

            # Sunday = Holiday
            if current_date.weekday() == 6:

                daily_reports.append(
                    DailyAttendanceResponse(
                        date=current_date,
                        day=current_date.strftime("%A"),
                        status="HOLIDAY",
                        present=[],
                        absent=[],
                    )
                )

                total_holidays += 1

                continue

            present = []
            absent = []

            # ---------------------------------
            # Check Every Active User
            # ---------------------------------
            for user in users:

                attendance = (
                    attendance_by_date_and_user.get(
                        (
                            current_date,
                            user.id,
                        )
                    )
                )

                employee = AttendanceEmployeeResponse(
                    employee_id=user.id,
                    employee_code=user.employee_code,
                    name=(
                        f"{user.first_name} "
                        f"{user.last_name}"
                    ),
                    department=(
                        user.department.name
                        if user.department
                        else None
                    ),
                    designation=(
                        user.designation.name
                        if user.designation
                        else None
                    ),
                    role=(
                        user.role.name
                        if user.role
                        else None
                    ),
                )

                if attendance is not None:
                    present.append(employee)
                    total_present += 1
                else:
                    absent.append(employee)
                    total_absent += 1

            # ---------------------------------
            # Apply Status Filter
            # ---------------------------------

            if status == "PRESENT":
                absent = []

            elif status == "ABSENT":
                present = []
            # ---------------------------------
            # Add Daily Report
            # ---------------------------------
            daily_reports.append(
                DailyAttendanceResponse(
                    date=current_date,
                    day=current_date.strftime("%A"),
                    status="WORKING_DAY",
                    present=present,
                    absent=absent,
                )
            )

        # ---------------------------------
        # Working Days
        # ---------------------------------
        total_working_days = (
            total_days - total_holidays
        )

        # ---------------------------------
        # Return Monthly Report
        # ---------------------------------
        return MonthlyAttendanceResponse(
            year=year,
            month=month,
            total_days=total_days,
            total_holidays=total_holidays,
            total_working_days=total_working_days,
            total_present=total_present,
            total_absent=total_absent,
            days=daily_reports,
        )

    async def get_lift_report(
        self,
        lift_code: str,
    ) -> LiftReportResponse:

        # ---------------------------------
        # Get Lift
        # ---------------------------------
        lift = await self.repository.get_lift_by_code(
            lift_code=lift_code
        )

        if lift is None:
            raise ValueError(
                "Lift not found."
            )

        # ---------------------------------
        # Get Phase History
        # ---------------------------------
        phase_history = (
            await self.repository.get_phase_history_by_lift(
                lift_id=lift.id
            )
        )

        # ---------------------------------
        # Get All Tasks
        # ---------------------------------
        tasks = await self.repository.get_tasks_by_lift(
            lift_id=lift.id
        )

        report_tasks = []

        for task in tasks:

            # ---------------------------------
            # Assigned Employee
            # ---------------------------------
            assigned_to = None

            if task.assigned_employee:
                assigned_to = (
                    f"{task.assigned_employee.first_name} "
                    f"{task.assigned_employee.last_name}"
                )

            # ---------------------------------
            # Assigned Manager
            # ---------------------------------
            assigned_by = None

            if task.assigned_manager:
                assigned_by = (
                    f"{task.assigned_manager.first_name} "
                    f"{task.assigned_manager.last_name}"
                )

            # ---------------------------------
            # Create Task Display Title
            # ---------------------------------
            if task.sub_category:
                task_title = (
                    f"{task.category} - "
                    f"{task.sub_category}"
                )
            else:
                task_title = task.category

            # ---------------------------------
            # Get Task Execution
            # ---------------------------------
            execution = (
                await self.repository.get_execution_by_task(
                    task_id=task.id
                )
            )

            report_execution = None

            if execution is not None:

                report_execution = (
                    ReportTaskExecutionResponse(
                        start_time=execution.start_time,
                        start_latitude=(
                            execution.start_latitude
                        ),
                        start_longitude=(
                            execution.start_longitude
                        ),
                        completed_time=(
                            execution.completed_time
                        ),
                        completed_latitude=(
                            execution.completed_latitude
                        ),
                        completed_longitude=(
                            execution.completed_longitude
                        ),
                        status=execution.status,
                        client_signature=(
                            execution.client_signature
                        ),
                        client_photo=(
                            execution.client_photo
                        ),
                    )
                )

            # ---------------------------------
            # Get Task Questions
            # ---------------------------------
            questions = (
                await self.repository.get_questions_by_task(
                    task_id=task.id
                )
            )

            questions_and_answers = []

            answers_by_question_id = {}

            # ---------------------------------
            # Get Task Answers
            # ---------------------------------
            if execution is not None:

                answers = (
                    await self.repository.get_answers_by_execution(
                        execution_id=execution.id
                    )
                )

                answers_by_question_id = {
                    answer.question_id: answer
                    for answer in answers
                }

            # ---------------------------------
            # Match Questions With Answers
            # ---------------------------------
            for question in questions:

                task_answer = (
                    answers_by_question_id.get(
                        question.id
                    )
                )

                questions_and_answers.append(
                    ReportTaskAnswerResponse(
                        question=question.question,
                        answer=(
                            task_answer.answer
                            if task_answer is not None
                            else None
                        ),
                    )
                )

            # ---------------------------------
            # Create Task Report
            # ---------------------------------
            report_tasks.append(
                ReportTaskResponse(
                    task_id=task.id,
                    task_number=task.task_number,
                    title=task_title,
                    status=task.status,
                    assigned_to=assigned_to,
                    assigned_by=assigned_by,
                    created_at=task.created_at,
                    due_date=task.due_date,
                    execution=report_execution,
                    questions_and_answers=questions_and_answers,
                )
            )

        # ---------------------------------
        # Convert Phase History
        # ---------------------------------
        report_phase_history = []

        for phase in phase_history:

            completed_by = None

            if phase.completed_by_user:
                completed_by = (
                    f"{phase.completed_by_user.first_name} "
                    f"{phase.completed_by_user.last_name}"
                )

            report_phase_history.append(
                ReportPhaseResponse(
                    phase_name=phase.phase.value,
                    completed_by=completed_by,
                    completed_at=phase.completed_at,
                )
            )

        # ---------------------------------
        # Latest Completed Phase
        # ---------------------------------
        current_phase = None

        if phase_history:
            current_phase = (
                phase_history[-1].phase.value
            )

        # ---------------------------------
        # Get All Tickets
        # ---------------------------------
        tickets = (
            await self.repository.get_tickets_by_lift(
                lift_id=lift.id
            )
        )

        report_tickets = []

        for ticket in tickets:

            report_tickets.append(
                ReportTicketResponse(
                    ticket_id=ticket.id,
                    ticket_number=ticket.ticket_number,
                    ticket_type=(
                        ticket.ticket_type.value
                    ),
                    priority=ticket.priority.value,
                    complaint_description=(
                        ticket.complaint_description
                    ),
                    status=ticket.status.value,
                    closing_remarks=(
                        ticket.closing_remarks
                    ),
                    created_at=ticket.created_at,
                    closed_at=ticket.closed_at,
                )
            )

        # ---------------------------------
        # Return Complete Lift Report
        # ---------------------------------
        return LiftReportResponse(
            lift_id=lift.id,
            lift_code=lift.lift_code,

            customer=ReportCustomerResponse(
                id=lift.customer.id,
                customer_code=(
                    lift.customer.customer_code
                ),
                name=lift.customer.project_name,
            ),

            current_phase=current_phase,

            phase_history=report_phase_history,

            tasks=report_tasks,

            tickets=report_tickets,
        )