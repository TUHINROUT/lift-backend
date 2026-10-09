from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class CustomerServiceReport(Base):
    __tablename__ = "customer_service_reports"

    id = Column(Integer, primary_key=True, index=True)
    sl_no = Column(String(50), nullable=True)
    report_date = Column(Date, default=date.today, nullable=True)

    customer_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    call_status = Column(String(50), default="AMC", nullable=True)
    instruction_from = Column(String(255), nullable=True)

    problem_report = Column(Text, nullable=True)
    make = Column(String(255), default="Jaguar Elevators Pvt Ltd", nullable=True)
    call_report_by = Column(String(255), nullable=True)
    call_report_date = Column(Date, nullable=True)
    call_report_time = Column(String(50), nullable=True)

    engineers_remarks = Column(Text, nullable=True)
    status_after_service = Column(String(100), default="Complete", nullable=True)
    defects_found = Column(Text, nullable=True)

    start_of_service = Column(String(50), nullable=True)
    end_of_service = Column(String(50), nullable=True)

    rating = Column(String(50), default="Satisfied", nullable=True)
    customer_remarks = Column(Text, nullable=True)
    customer_contact_name = Column(String(255), nullable=True)
    customer_designation = Column(String(100), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_email = Column(String(255), nullable=True)
    feedback_date = Column(Date, nullable=True)
    place = Column(String(100), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    engineer_signature = Column(String(500), nullable=True)
    customer_signature = Column(String(500), nullable=True)

    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    technician = relationship("User", foreign_keys=[technician_id])

    # Plain naive UTC timestamps to match PostgreSQL TIMESTAMP WITHOUT TIME ZONE
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)