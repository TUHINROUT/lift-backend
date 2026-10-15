import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime,
    ForeignKey, Enum, Numeric, JSON
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class LeadStageEnum(str, enum.Enum):
    FRESH_LEAD = "Fresh Lead"
    POSITIVE_FOLLOWUP = "Positive Follow-up"
    DO_NOT_PICK = "Do Not Pick"
    MEETING_FIXED = "Meeting Fixed"
    NOT_INTERESTED = "Not Interested"
    MEETING_ATTENDED = "Meeting Attended"
    FOLLOWUP_MEETING = "Follow-up Meeting"
    SALE_DONE = "Sale Done"
    ORDER_LOST = "Order Lost"


class LeadPriorityEnum(str, enum.Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LeadSourceEnum(str, enum.Enum):
    CSV_UPLOAD = "CSV_UPLOAD"
    EXCEL_UPLOAD = "EXCEL_UPLOAD"
    MANUAL_OFFLINE = "MANUAL_OFFLINE"
    PUBLIC_WEB_PORTAL = "PUBLIC_WEB_PORTAL"
    WHATSAPP_CAMPAIGN = "WHATSAPP_CAMPAIGN"


class DepartmentWorkflowEnum(str, enum.Enum):
    SALES = "SALES"
    FINANCE = "FINANCE"
    OPERATION = "OPERATION"
    SERVICE = "SERVICE"
    COMPLETED = "COMPLETED"


class CRMLead(Base):
    __tablename__ = "crm_leads"

    id = Column(Integer, primary_key=True, index=True)
    lead_code = Column(String(50), unique=True, index=True, nullable=False)

    # Basic Contact Data
    lead_name = Column(String(200), nullable=False, index=True)
    lead_number = Column(String(30), nullable=False, index=True)
    lead_email = Column(String(120), nullable=True)
    city = Column(String(100), default="Bhubaneswar", nullable=False)
    address = Column(Text, nullable=True)

    # Technical Elevator Specifications
    number_of_stops = Column(String(50), nullable=True)
    passenger_capacity = Column(String(50), nullable=True)
    shaft_width = Column(String(50), nullable=True)
    shaft_depth = Column(String(50), nullable=True)
    pit_height = Column(String(50), nullable=True)

    # Status, Priority & Filtering Flags
    stage = Column(Enum(LeadStageEnum), default=LeadStageEnum.FRESH_LEAD, nullable=False, index=True)
    priority = Column(Enum(LeadPriorityEnum), default=LeadPriorityEnum.HIGH, nullable=False, index=True)
    source = Column(Enum(LeadSourceEnum), default=LeadSourceEnum.MANUAL_OFFLINE, nullable=False)
    is_completed_data = Column(Boolean, default=False, nullable=False, index=True)

    # Ownership & Assignment
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_at = Column(DateTime, nullable=True)

    # Reminders
    next_followup_date = Column(DateTime, nullable=True, index=True)
    reminder_note = Column(String(255), nullable=True)

    # Multi-Department Workflow Tracking
    current_department = Column(Enum(DepartmentWorkflowEnum), default=DepartmentWorkflowEnum.SALES, nullable=False, index=True)

    # Finance Department Tracking
    deal_value = Column(Numeric(12, 2), nullable=True)
    advance_payment_received = Column(Boolean, default=False)
    finance_approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    finance_notes = Column(Text, nullable=True)

    # Operation Department Tracking
    site_ready_for_installation = Column(Boolean, default=False)
    operation_assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operation_notes = Column(Text, nullable=True)

    # Service Department Tracking
    service_incharge_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_contractor_name = Column(String(120), nullable=True)
    assigned_technician_name = Column(String(120), nullable=True)
    commissioning_completed = Column(Boolean, default=False)
    service_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="joined")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], lazy="joined")
    finance_approver = relationship("User", foreign_keys=[finance_approved_by_id], lazy="joined")
    operation_incharge = relationship("User", foreign_keys=[operation_assigned_to_id], lazy="joined")
    service_incharge = relationship("User", foreign_keys=[service_incharge_id], lazy="joined")

    activities = relationship(
        "CRMLeadActivity",
        back_populates="lead",
        cascade="all, delete-orphan",
        order_by="desc(CRMLeadActivity.created_at)",
        lazy="selectin"
    )

    def check_completeness(self) -> bool:
        has_basic = bool(self.lead_name and self.lead_number and self.city)
        has_specs = bool(self.number_of_stops and self.passenger_capacity)
        return has_basic and has_specs


class CRMLeadActivity(Base):
    __tablename__ = "crm_lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    department = Column(String(50), default="SALES", nullable=False)
    previous_stage = Column(String(50), nullable=True)
    new_stage = Column(String(50), nullable=True)
    action_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lead = relationship("CRMLead", back_populates="activities")
    performed_by = relationship("User", foreign_keys=[performed_by_id], lazy="joined")


class CRMProposal(Base):
    __tablename__ = "crm_proposals"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), unique=True, nullable=False)
    offer_no = Column(String(100), unique=True, index=True, nullable=False)
    date_str = Column(String(50), nullable=False)
    proposal_data = Column(JSON, nullable=False)
    total_amount = Column(Float, default=913700.0)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    sent_to = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead = relationship("CRMLead", backref="saved_proposal")


class CRMNotification(Base):
    __tablename__ = "crm_notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="NOTIFICATION", nullable=False)
    is_urgent = Column(Boolean, default=False, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    recipient = relationship("User", foreign_keys=[recipient_id], lazy="joined")
    sender = relationship("User", foreign_keys=[sender_id], lazy="joined")
    lead = relationship("CRMLead", foreign_keys=[lead_id], lazy="joined")