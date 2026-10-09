from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.common.enums import LiftPhase


class LiftPhaseCompleteRequest(BaseModel):
    phase: LiftPhase


class LiftPhaseHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lift_id: int
    phase: LiftPhase
    completed_by: int
    completed_at: datetime

class LiftCurrentPhaseResponse(BaseModel):
    lift_id: int
    current_phase: LiftPhase | None