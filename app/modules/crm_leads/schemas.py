from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.modules.crm_leads.models import (
    LeadStageEnum, LeadSourceEnum, LeadPriorityEnum, DepartmentWorkflowEnum
)


class LeadCreateManual(BaseModel):
    lead_name: str
    lead_number: str
    lead_email: Optional[str] = None
    city: str = "Bhubaneswar"
    address: Optional[str] = None

    # Specifications
    number_of_stops: Optional[str] = None
    passenger_capacity: Optional[str] = None
    shaft_width: Optional[str] = None
    shaft_depth: Optional[str] = None
    pit_height: Optional[str] = None

    stage: LeadStageEnum = LeadStageEnum.FRESH_LEAD
    priority: LeadPriorityEnum = LeadPriorityEnum.HIGH
    next_followup_date: Optional[datetime] = None
    reminder_note: Optional[str] = None


class PublicWebLeadCreate(BaseModel):
    lead_name: str
    lead_number: str
    lead_email: Optional[str] = None
    city: str = "Bhubaneswar"
    address: Optional[str] = None
    number_of_stops: Optional[str] = None
    passenger_capacity: Optional[str] = None
    requirements: Optional[str] = None


class LeadAssignRequest(BaseModel):
    sales_rep_id: Optional[int] = None


class LeadStageUpdateRequest(BaseModel):
    new_stage: LeadStageEnum
    activity_remarks: str
    deal_value: Optional[float] = None
    next_followup_date: Optional[datetime] = None


class FinanceHandoffRequest(BaseModel):
    deal_value: float
    advance_payment_received: bool
    finance_officer_id: Optional[int] = None
    remarks: str


class OperationHandoffRequest(BaseModel):
    operation_incharge_id: Optional[int] = None
    site_ready_for_installation: bool
    remarks: str


class ServiceHandoffRequest(BaseModel):
    service_incharge_id: Optional[int] = None
    assigned_contractor_name: Optional[str] = "GUIDEX Direct"
    assigned_technician_name: Optional[str] = "Admin / Field Engineer"
    remarks: str


class ServiceCommissioningCompleteRequest(BaseModel):
    amc_contract_number: Optional[str] = "AMC-2026-COMPREHENSIVE"
    amc_start_date: Optional[datetime] = None
    amc_end_date: Optional[datetime] = None
    remarks: str = "Lift commissioned, test load approved, and handed over to client."


class AnnouncementCreate(BaseModel):
    title: str = Field(..., example="Record Lead Conversion!")
    message: str = Field(..., example="5 Lifts Closed in Patia Project by Sales Team!")
    is_urgent: bool = True


class UserSimpleOut(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class ActivityOut(BaseModel):
    id: int
    department: str = "SALES"
    action_type: str
    previous_stage: Optional[str] = None
    new_stage: Optional[str] = None
    description: str
    performed_by: Optional[UserSimpleOut] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeadDetailOut(BaseModel):
    id: int
    lead_code: str
    lead_name: str
    lead_number: str
    lead_email: Optional[str] = None
    city: str = "Bhubaneswar"
    address: Optional[str] = None
    number_of_stops: Optional[str] = None
    passenger_capacity: Optional[str] = None
    shaft_width: Optional[str] = None
    shaft_depth: Optional[str] = None
    pit_height: Optional[str] = None
    stage: LeadStageEnum = LeadStageEnum.FRESH_LEAD
    priority: LeadPriorityEnum = LeadPriorityEnum.HIGH
    source: LeadSourceEnum = LeadSourceEnum.MANUAL_OFFLINE
    is_completed_data: bool = False
    current_department: DepartmentWorkflowEnum = DepartmentWorkflowEnum.SALES

    deal_value: Optional[float] = None
    advance_payment_received: Optional[bool] = False
    site_ready_for_installation: Optional[bool] = False
    assigned_contractor_name: Optional[str] = None
    assigned_technician_name: Optional[str] = None
    commissioning_completed: Optional[bool] = False

    created_by: Optional[UserSimpleOut] = None
    assigned_to: Optional[UserSimpleOut] = None
    assigned_at: Optional[datetime] = None
    next_followup_date: Optional[datetime] = None
    reminder_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    activities: List[ActivityOut] = []

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    recipient_id: Optional[int] = None
    title: str
    message: str
    notification_type: str = "NOTIFICATION"
    is_urgent: bool = False
    is_read: bool = False
    lead_id: Optional[int] = None
    created_at: datetime
    sender: Optional[UserSimpleOut] = None

    class Config:
        from_attributes = True


class ExecutiveDashboardAnalytics(BaseModel):
    total_leads: int
    fresh_leads: int
    meetings_in_progress: int
    sale_done_count: int
    total_revenue_won: float
    pending_followups_today: int
    department_distribution: Dict[str, int]


# ==================== STEPPER LOGISTICAL TRACKING SCHEMAS ====================

class SubMilestoneEvent(BaseModel):
    title: str
    description: Optional[str] = None
    timestamp: datetime
    performed_by: Optional[str] = None
    department: str


class MainMilestoneStep(BaseModel):
    step_key: str
    title: str
    status: str
    completed_at: Optional[datetime] = None
    sub_events: List[SubMilestoneEvent] = []


class LeadTrackerTimelineResponse(BaseModel):
    lead_id: int
    lead_code: str
    lead_name: str
    city: str
    current_department: str
    overall_stage: str
    deal_value: Optional[float] = None
    advance_payment_received: bool = False
    site_ready_for_installation: bool = False
    assigned_contractor_name: Optional[str] = None
    assigned_technician_name: Optional[str] = None
    lift_specifications: Dict[str, str]
    milestones: List[MainMilestoneStep]


# ==================== PROPOSAL & SHARING SCHEMAS ====================

class ProposalUpdatePayload(BaseModel):
    customer_name: Optional[str] = None
    site_address: Optional[str] = None
    customer_contact: Optional[str] = None
    subject: Optional[str] = None
    car_travel: Optional[str] = None
    lift_well: Optional[str] = None
    cost_per_lift: Optional[float] = None
    price_in_words: Optional[str] = None
    validity_days: Optional[int] = None


class ProposalShareRequest(BaseModel):
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    share_channel: Optional[str] = "WHATSAPP"
    custom_note: Optional[str] = None