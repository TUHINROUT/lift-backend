from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import LiftPhase
from app.modules.lift_phases.models import LiftPhaseHistory
from app.modules.lift_phases.repository import LiftPhaseRepository
from app.modules.lifts.repository import LiftRepository
from app.modules.users.repository import UsersRepository
from app.services.email import send_email


class LiftPhaseService:

    def __init__(self, db: AsyncSession):
        self.repository = LiftPhaseRepository(db)
        self.lift_repository = LiftRepository(db)
        self.users_repository = UsersRepository(db)

    async def complete_phase(
        self,
        lift_id: int,
        phase: LiftPhase,
        completed_by: int,
    ) -> LiftPhaseHistory:

        lift = await self.lift_repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        existing_history = (
            await self.repository.get_by_lift_and_phase(
                lift_id,
                phase,
            )
        )

        if existing_history:
            raise ValueError(
                f"{phase.value} phase is already completed."
            )

        completed_at = datetime.now(timezone.utc)

        history = LiftPhaseHistory(
            lift_id=lift_id,
            phase=phase,
            completed_by=completed_by,
            completed_at=completed_at,
        )

        history = await self.repository.create(history)

        if phase in (
            LiftPhase.CONSULTATION,
            LiftPhase.HANDOVER,
        ):
            recipients = (
                await self.users_repository
                .get_active_admins_and_managers()
            )

            email_addresses = {
                user.email
                for user in recipients
                if user.email
            }

            if lift.customer and lift.customer.email:
                email_addresses.add(lift.customer.email)

            subject = (
                f"Lift {lift.lift_code} - "
                f"{phase.value} Completed"
            )

            body = (
                f"Lift Phase Update\n\n"
                f"Lift Code: {lift.lift_code}\n"
                f"Phase: {phase.value}\n"
                f"Completed At: {completed_at}\n"
            )
            print("\nLIFT PHASE EMAIL RECIPIENTS:")
            for email in email_addresses:
                print(f"Sending phase email to: {email}")

            for email in email_addresses:
                send_email(
                    to_email=email,
                    subject=subject,
                    body=body,
                )

        return history
    async def get_current_phase(
        self,
        lift_id: int,
    ) -> LiftPhaseHistory | None:

        lift = await self.lift_repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        histories = await self.repository.get_by_lift(lift_id)

        if not histories:
            return None

        return histories[-1].phase