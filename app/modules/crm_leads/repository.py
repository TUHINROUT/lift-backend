import csv
import io
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
import openpyxl

from app.modules.crm_leads.models import (
    CRMLead, CRMLeadActivity, CRMNotification,
    LeadStageEnum, LeadSourceEnum, LeadPriorityEnum, DepartmentWorkflowEnum
)
from app.modules.crm_leads.schemas import LeadCreateManual, PublicWebLeadCreate


class CRMLeadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_lead_code(self) -> str:
        return f"LEAD-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"

    async def get_by_id(self, lead_id: int) -> Optional[CRMLead]:
        stmt = (
            select(CRMLead)
            .filter(CRMLead.id == lead_id)
            .options(
                selectinload(CRMLead.created_by),
                selectinload(CRMLead.assigned_to),
                selectinload(CRMLead.activities).selectinload(CRMLeadActivity.performed_by)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_lead(
        self,
        lead_data: LeadCreateManual,
        user_id: Optional[int] = None,
        source: LeadSourceEnum = LeadSourceEnum.MANUAL_OFFLINE
    ) -> CRMLead:
        # Duplicate detection by phone number
        clean_phone = "".join(filter(str.isdigit, lead_data.lead_number))
        dup_filter = []
        if len(clean_phone) >= 10:
            dup_filter.append(CRMLead.lead_number.contains(clean_phone[-10:]))
        else:
            dup_filter.append(CRMLead.lead_number == lead_data.lead_number.strip())

        if lead_data.lead_email:
            dup_filter.append(CRMLead.lead_email == lead_data.lead_email.strip().lower())

        dup_stmt = select(CRMLead).filter(or_(*dup_filter))
        dup_res = await self.db.execute(dup_stmt)
        existing_lead = dup_res.scalars().first()

        flag_note = lead_data.reminder_note
        if existing_lead:
            flag_note = f"FLAGGED DUPLICATE: Exists as {existing_lead.lead_code} ({existing_lead.lead_name})"

        lead = CRMLead(
            lead_code=self.generate_lead_code(),
            lead_name=lead_data.lead_name.strip(),
            lead_number=lead_data.lead_number.strip(),
            lead_email=lead_data.lead_email.strip().lower() if lead_data.lead_email else None,
            city=lead_data.city.strip() if lead_data.city else "Bhubaneswar",
            address=lead_data.address.strip() if lead_data.address else None,
            number_of_stops=lead_data.number_of_stops.strip() if lead_data.number_of_stops else None,
            passenger_capacity=lead_data.passenger_capacity.strip() if lead_data.passenger_capacity else None,
            shaft_width=lead_data.shaft_width.strip() if lead_data.shaft_width else None,
            shaft_depth=lead_data.shaft_depth.strip() if lead_data.shaft_depth else None,
            pit_height=lead_data.pit_height.strip() if lead_data.pit_height else None,
            stage=lead_data.stage,
            priority=lead_data.priority,
            source=source,
            created_by_id=user_id,
            assigned_to_id=user_id,  # Admin defaults as owner
            assigned_at=datetime.utcnow() if user_id else None,
            advance_payment_received=False,
            site_ready_for_installation=False,
            commissioning_completed=False,
            current_department=DepartmentWorkflowEnum.SALES,
            next_followup_date=lead_data.next_followup_date,
            reminder_note=flag_note,
        )
        lead.is_completed_data = lead.check_completeness()
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)

        try:
            activity = CRMLeadActivity(
                lead_id=lead.id,
                performed_by_id=user_id,
                department="SALES",
                action_type="CREATION",
                previous_stage=None,
                new_stage=lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage),
                description=f"Ingested via {source.value}. Specs Completed: {lead.is_completed_data}" + (" [DUPLICATE DETECTED]" if existing_lead else "")
            )
            self.db.add(activity)
            await self.db.commit()
        except Exception:
            await self.db.rollback()

        return await self.get_by_id(lead.id)

    async def create_public_portal_lead(self, payload: PublicWebLeadCreate) -> CRMLead:
        lead_dto = LeadCreateManual(
            lead_name=payload.lead_name,
            lead_number=payload.lead_number,
            lead_email=payload.lead_email,
            city=payload.city,
            address=payload.address,
            number_of_stops=payload.number_of_stops,
            passenger_capacity=payload.passenger_capacity,
            stage=LeadStageEnum.FRESH_LEAD,
            priority=LeadPriorityEnum.HIGH,
            reminder_note=payload.requirements
        )
        return await self.create_lead(lead_dto, user_id=None, source=LeadSourceEnum.PUBLIC_WEB_PORTAL)

    async def add_activity(
        self,
        lead: CRMLead,
        user_id: Optional[int],
        action_type: str,
        description: str,
        department: str = "SALES",
        previous_stage: Optional[str] = None,
        new_stage: Optional[str] = None
    ) -> CRMLeadActivity:
        activity = CRMLeadActivity(
            lead_id=lead.id,
            performed_by_id=user_id,
            department=department,
            action_type=action_type,
            previous_stage=previous_stage,
            new_stage=new_stage,
            description=description
        )
        self.db.add(activity)
        await self.db.commit()
        return activity

    async def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "NOTIFICATION",
        is_urgent: bool = False,
        recipient_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        lead_id: Optional[int] = None
    ) -> CRMNotification:
        notification = CRMNotification(
            recipient_id=recipient_id,
            sender_id=sender_id,
            lead_id=lead_id,
            title=title,
            message=message,
            notification_type=notification_type,
            is_urgent=is_urgent,
            is_read=False
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def process_file_records(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: Optional[int]
    ) -> Tuple[int, int]:
        records: List[Dict[str, Any]] = []

        if filename.endswith(".csv"):
            try:
                decoded = file_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                decoded = file_bytes.decode("latin-1")
            reader = csv.DictReader(io.StringIO(decoded))
            records = list(reader)
            source_type = LeadSourceEnum.CSV_UPLOAD

        elif filename.endswith((".xlsx", ".xls")):
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            if not rows or len(rows) < 2:
                return (0, 0)
            headers = [str(cell or "").strip() for cell in rows[0]]
            for row in rows[1:]:
                record_dict = {}
                for idx, val in enumerate(row):
                    if idx < len(headers) and headers[idx]:
                        record_dict[headers[idx]] = str(val or "").strip()
                records.append(record_dict)
            source_type = LeadSourceEnum.EXCEL_UPLOAD
        else:
            return (0, 0)

        imported = 0
        completed = 0

        for row in records:
            name = (
                row.get("Customer Name") or 
                row.get("Customer Name ") or 
                row.get("Lead Name") or 
                row.get("Client Name") or 
                row.get("Name")
            )
            phone = (
                row.get("Phone Number") or 
                row.get("Phone Number ") or 
                row.get("Lead Number") or 
                row.get("Phone") or 
                row.get("Mobile")
            )
            if not name or not phone:
                continue

            stops = (
                row.get("No of Floor") or 
                row.get("No of Floor ") or 
                row.get("Number of Stops") or 
                row.get("Stops")
            )

            shaft_w = row.get("Shaft Width") or row.get("Width")
            shaft_d = row.get("Shaft Depth") or row.get("Depth")
            combined_shaft = (
                row.get("Shaft Dimension (W X D)") or 
                row.get("Shaft Dimension (W X D) ") or 
                row.get("Shaft Dimension")
            )
            if combined_shaft and not (shaft_w and shaft_d):
                dim_str = str(combined_shaft).strip().lower()
                for delimiter in ["x", "*", "by", " "]:
                    if delimiter in dim_str:
                        parts = [p.strip() for p in dim_str.split(delimiter) if p.strip()]
                        if len(parts) >= 2:
                            shaft_w = f"{parts[0]} mm"
                            shaft_d = f"{parts[1]} mm"
                            break

            remarks_parts = []
            for key in ["Remarks SP", "Remarks", "Remarks ", "Nikita", "Interested ?", "Called ?"]:
                val = row.get(key)
                if val and str(val).strip() and str(val).lower() != "nan":
                    remarks_parts.append(f"{key}: {str(val).strip()}")
            combined_remarks = " | ".join(remarks_parts) if remarks_parts else None

            priority_val = row.get("Priority Lead") or row.get("Priority")
            mapped_priority = LeadPriorityEnum.HIGH
            if priority_val:
                try:
                    p_num = int(str(priority_val).strip())
                    if p_num <= 2:
                        mapped_priority = LeadPriorityEnum.URGENT
                    elif p_num == 3:
                        mapped_priority = LeadPriorityEnum.HIGH
                    else:
                        mapped_priority = LeadPriorityEnum.MEDIUM
                except Exception:
                    mapped_priority = LeadPriorityEnum.HIGH

            lead_dto = LeadCreateManual(
                lead_name=str(name).strip().replace("\n", " "),
                lead_number=str(phone).strip().replace("\n", " "),
                lead_email=row.get("Email") or row.get("lead_email"),
                city=str(row.get("City") or "Bhubaneswar").strip(),
                address=str(row.get("Address") or row.get("Address ") or "").strip() or None,
                number_of_stops=str(stops).strip() if stops else None,
                passenger_capacity=row.get("Passenger Capacity") or "6 Person / 408 kg",
                shaft_width=str(shaft_w).strip() if shaft_w else None,
                shaft_depth=str(shaft_d).strip() if shaft_d else None,
                pit_height=str(row.get("Pit Size") or row.get("Pit Height") or "1500 mm").strip(),
                stage=LeadStageEnum.FRESH_LEAD,
                priority=mapped_priority,
                reminder_note=combined_remarks
            )
            lead = await self.create_lead(lead_dto, user_id=user_id, source=source_type)
            imported += 1
            if lead.is_completed_data:
                completed += 1

        return (imported, completed)

    async def get_analytics(self) -> Dict[str, Any]:
        total_stmt = select(func.count(CRMLead.id))
        total = (await self.db.execute(total_stmt)).scalar() or 0

        fresh_stmt = select(func.count(CRMLead.id)).filter(CRMLead.stage == LeadStageEnum.FRESH_LEAD)
        fresh = (await self.db.execute(fresh_stmt)).scalar() or 0

        meetings_stmt = select(func.count(CRMLead.id)).filter(
            CRMLead.stage.in_([
                LeadStageEnum.MEETING_FIXED,
                LeadStageEnum.MEETING_ATTENDED,
                LeadStageEnum.FOLLOWUP_MEETING
            ])
        )
        meetings = (await self.db.execute(meetings_stmt)).scalar() or 0

        won_stmt = select(func.count(CRMLead.id)).filter(CRMLead.stage == LeadStageEnum.SALE_DONE)
        won = (await self.db.execute(won_stmt)).scalar() or 0

        revenue_stmt = select(func.coalesce(func.sum(CRMLead.deal_value), 0.0)).filter(
            CRMLead.stage == LeadStageEnum.SALE_DONE
        )
        revenue = (await self.db.execute(revenue_stmt)).scalar() or 0.0

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        followups_stmt = select(func.count(CRMLead.id)).filter(
            CRMLead.next_followup_date >= today_start,
            CRMLead.next_followup_date <= today_end
        )
        followups_today = (await self.db.execute(followups_stmt)).scalar() or 0

        dept_dist = {}
        for dept in [DepartmentWorkflowEnum.SALES, DepartmentWorkflowEnum.FINANCE, DepartmentWorkflowEnum.OPERATION, DepartmentWorkflowEnum.SERVICE]:
            stmt = select(func.count(CRMLead.id)).filter(CRMLead.current_department == dept)
            dept_dist[dept.value] = (await self.db.execute(stmt)).scalar() or 0

        return {
            "total_leads": total,
            "fresh_leads": fresh,
            "meetings_in_progress": meetings,
            "sale_done_count": won,
            "total_revenue_won": float(revenue),
            "pending_followups_today": followups_today,
            "department_distribution": dept_dist
        }