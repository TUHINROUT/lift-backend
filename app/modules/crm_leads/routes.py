from datetime import datetime
from typing import List, Optional, Any
import urllib.parse
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile,
    File, status, WebSocket, WebSocketDisconnect, Query, BackgroundTasks,
    Body, Response, Request
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.crm_leads.models import (
    CRMLead, CRMLeadActivity, CRMNotification,
    LeadStageEnum, DepartmentWorkflowEnum, LeadPriorityEnum
)
from app.modules.crm_leads.repository import CRMLeadRepository
from app.modules.crm_leads.websocket_manager import crm_ws_manager
from app.modules.crm_leads.proposal_pdf_generator import generate_guidex_9page_pdf
from app.modules.crm_leads.schemas import (
    LeadCreateManual,
    PublicWebLeadCreate,
    LeadAssignRequest,
    LeadStageUpdateRequest,
    FinanceHandoffRequest,
    OperationHandoffRequest,
    ServiceHandoffRequest,
    ServiceCommissioningCompleteRequest,
    AnnouncementCreate,
    LeadDetailOut,
    NotificationOut,
    ExecutiveDashboardAnalytics,
    LeadTrackerTimelineResponse,
    MainMilestoneStep,
    SubMilestoneEvent,
    ProposalUpdatePayload,
    ProposalShareRequest
)

router = APIRouter(prefix="/crm/leads", tags=["CRM Lead Management"])


async def _extract_user_id(current_user: Any, db: AsyncSession) -> Optional[int]:
    """Safely extracts the user ID across model instances, dicts, or fallback queries."""
    uid = getattr(current_user, "id", None)
    if uid is None and isinstance(current_user, dict):
        uid = current_user.get("id")
    if not uid:
        stmt = select(User.id).limit(1)
        res = await db.execute(stmt)
        uid = res.scalar()
    return uid


def _build_lead_proposal_dict(lead: CRMLead) -> dict:
    """Builds full 9-page Guidex quotation dictionary dynamically from CRMLead record."""
    offer_number = f"GDX/{datetime.utcnow().strftime('%m%Y')}/{lead.id + 290}"
    deal_price = float(lead.deal_value) if lead.deal_value else 913700.00

    stops_display = lead.number_of_stops or "G+3"
    stops_num = 4
    if "g+" in stops_display.lower():
        try:
            stops_num = int(stops_display.lower().split("g+")[1]) + 1
        except Exception:
            stops_num = 4
    floor_rise_meters = f"{stops_num * 3.0:.0f} Meters"

    shaft_w = lead.shaft_width or "1800 mm"
    shaft_d = lead.shaft_depth or "1600 mm"
    shaft_display = f"{shaft_w} x {shaft_d}"

    letter_data = {
        "offer_no": offer_number,
        "date": datetime.utcnow().strftime("%d/%m/%Y"),
        "customer_name": lead.lead_name,
        "site_address": f"{lead.address or 'Kalinga Nagar'}, {lead.city}, Odisha",
        "customer_contact": lead.lead_number,
        "subject": f"Supply, Installation, Testing and Commissioning of 01 (One) Nos. “GUIDEX” Make Elevator Proposal for your Proposed Project.",
        "office_contact": "+91 9668654365",
        "validity_days": 30
    }

    tech_specs = {
        "no_of_unit": "01 (One)",
        "type": "06 PASSENGERS",
        "load": lead.passenger_capacity or "408 KG",
        "speed": "1 MPS",
        "control": "Microprocessor VVVF",
        "car_travel": stops_display,
        "floor_rise": floor_rise_meters,
        "no_of_opening": stops_num,
        "no_of_stops": stops_num,
        "operation": "Gearless / Machine Room Less",
        "car_finish": "SS Hairline",
        "car_enclosure": "1.2MM",
        "car_entrance_door": "SS Hairline",
        "clear_door_opening": "700mm X 2000mm / 800mm X 2000mm",
        "lift_well": shaft_display,
        "car_inside": "1000mm X 1100mm",
        "overhead": "4200mm",
        "pit_depth": lead.pit_height or "1500mm",
        "cabin_finish": "Hairline Stainless Steel",
        "door_finish": "Side Opening Door with SS Hairline Finish",
        "car_ceiling_finish": "SS Mirror (1.2MM Grade 304)",
        "handrails": "SS Mirror Finish on rear Panel",
        "ventilation": "Cross Flow fan",
        "flooring": "PVC / Wooden",
        "machine_unit": "3 Phase PM Gearless Motor (Montanari)",
        "power_supply": "AC 440 V , 3 Phase 50 Hz",
        "stabilizer": "Yes"
    }

    pricing = {
        "no_of_lift": 1,
        "cost_per_lift": deal_price,
        "total_price": deal_price,
        "price_in_words": "Nine Lakhs Thirteen Thousand Seven Hundred Only" if deal_price == 913700.00 else f"INR {deal_price:,.2f}"
    }

    brands_list = [
        {"parts": "Cabin", "grade_brand": "SS Hairline 304 Grade"},
        {"parts": "Motor", "grade_brand": "Montanari (Life Time Warranty)"},
        {"parts": "COP/ LOP", "grade_brand": "GUIDEX Make"},
        {"parts": "Rope", "grade_brand": "Usha Martin"},
        {"parts": "Door", "grade_brand": "Fermator/ NBSL/ Wittur"},
        {"parts": "Warranty / AMC", "grade_brand": "1 Year / 2 Years"},
        {"parts": "Guide Rail", "grade_brand": "Marazzi / Kamachi Imported"},
        {"parts": "Door Sensors", "grade_brand": "Weco"},
        {"parts": "Controller", "grade_brand": "Monarch Drive / Arkel"}
    ]

    return {
        "company_header": {
            "name": "GUIDEX ELEVATOR PVT. LTD.",
            "location": "Bhubaneswar, Odisha",
            "email": "info@guidexelevator.com",
            "website": "www.guidexelevator.com",
            "office_contact": "+91 9668654365"
        },
        "page_1_cover": {
            "company_name": "GUIDEX ELEVATOR PVT. LTD.",
            "tagline": "The Safest Elevator of India",
            "standard": "As per IS17900",
            "website": "www.guidexelevator.com",
            "email": "info@guidexelevator.com"
        },
        "page_2_letter": letter_data,
        "page_3_and_4_technical_specifications": tech_specs,
        "page_5_features_and_pricing": {
            "main_features": [
                {"name": "Hassle Free Comprehensive maintenance for 1 year", "included": True},
                {"name": "Fire rated landing doors - 60 Mins", "included": True},
                {"name": "Door with mechanical lock", "included": True},
                {"name": "Anti Nuisance Car Call Protection", "included": True},
                {"name": "Overspeed Protection for Lift Car (OSG)", "included": True},
                {"name": "Manual Rescue Operation", "included": True}
            ],
            "safety_features": [
                {"name": "Overload protection", "included": True},
                {"name": "Emergency Alarm", "included": True},
                {"name": "Infrared Door Protection", "included": True},
                {"name": "Emergency Stop Switch", "included": True},
                {"name": "Door Open & Close Button", "included": True},
                {"name": "ARD System (Automatic Rescue Device)", "included": True}
            ],
            "price_schedule": pricing
        },
        "page_7_and_8_specifications_and_brands": {
            "delivery_timeline": "Estimated total time for delivery, installation, and commissioning is 3 months.",
            "warranty": "12 months warranty from date of successful commissioning.",
            "brands": brands_list
        },
        "page_9_maintenance_contract": {
            "contract_terms": {
                "duration": "1st Year, 2nd Year CMC / AMC",
                "price": "Free",
                "no_of_service_per_year": "8 Service / Year",
                "work_details": "Safety Check, Maintenance, Cleaning"
            }
        },
        "offer_details": letter_data,
        "technical_specifications": tech_specs,
        "price_schedule": pricing
    }


# ==================== WEBSOCKET LIVE STREAM ====================

@router.websocket("/ws/{user_id}")
async def crm_realtime_websocket(
    websocket: WebSocket,
    user_id: int,
    is_admin: bool = Query(False)
):
    await crm_ws_manager.connect(websocket, user_id=user_id, is_admin=is_admin)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        crm_ws_manager.disconnect(websocket, user_id=user_id, is_admin=is_admin)


# ==================== PUBLIC INGESTION PORTAL ====================

@router.post("/public-ingest", response_model=LeadDetailOut, status_code=status.HTTP_201_CREATED)
async def public_lead_portal(
    payload: PublicWebLeadCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    repo = CRMLeadRepository(db)
    lead = await repo.create_public_portal_lead(payload)

    await repo.create_notification(
        title="⚡ Online Lead Ingested!",
        message=f"Inquiry from {lead.lead_name} ({lead.city}). Stops: {lead.number_of_stops or 'N/A'}",
        notification_type="ONLINE_LEAD",
        is_urgent=True,
        lead_id=lead.id
    )

    background_tasks.add_task(
        crm_ws_manager.broadcast_to_admins,
        {
            "event": "ONLINE_LEAD_ALERT",
            "title": "⚡ New Online Lead!",
            "lead_id": lead.id,
            "lead_code": lead.lead_code,
            "lead_name": lead.lead_name,
            "city": lead.city,
            "sound": "alert_chime"
        }
    )

    stmt = (
        select(CRMLead)
        .options(
            selectinload(CRMLead.created_by),
            selectinload(CRMLead.assigned_to),
            selectinload(CRMLead.activities).selectinload(CRMLeadActivity.performed_by)
        )
        .filter(CRMLead.id == lead.id)
    )
    res = await db.execute(stmt)
    return res.scalars().first()


# ==================== SALES ACTIONS ====================

@router.post("/manual", response_model=LeadDetailOut, status_code=status.HTTP_201_CREATED)
async def create_manual_lead(
    payload: LeadCreateManual,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    user_id = await _extract_user_id(current_user, db)
    repo = CRMLeadRepository(db)

    try:
        lead = await repo.create_lead(payload, user_id=user_id)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create lead: {str(exc)}"
        )

    user_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "Admin")
    background_tasks.add_task(
        crm_ws_manager.broadcast_to_admins,
        {
            "event": "NEW_OFFLINE_LEAD",
            "lead_code": lead.lead_code,
            "lead_name": lead.lead_name,
            "created_by": user_name
        }
    )

    stmt = (
        select(CRMLead)
        .options(
            selectinload(CRMLead.created_by),
            selectinload(CRMLead.assigned_to),
            selectinload(CRMLead.activities).selectinload(CRMLeadActivity.performed_by)
        )
        .filter(CRMLead.id == lead.id)
    )
    res = await db.execute(stmt)
    return res.scalars().first()


@router.post("/upload-file", status_code=status.HTTP_200_OK)
async def upload_leads_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    allowed_exts = (".csv", ".xlsx", ".xls")
    if not any(file.filename.lower().endswith(ext) for ext in allowed_exts):
        raise HTTPException(status_code=400, detail="Only .csv, .xlsx, or .xls files accepted.")

    user_id = await _extract_user_id(current_user, db)
    content = await file.read()
    repo = CRMLeadRepository(db)
    imported, completed = await repo.process_file_records(content, file.filename.lower(), user_id=user_id)

    await repo.create_notification(
        title="Spreadsheet Ingested",
        message=f"{imported} leads uploaded ({completed} ready for assignment).",
        notification_type="SYSTEM",
        sender_id=user_id
    )

    background_tasks.add_task(
        crm_ws_manager.broadcast_to_admins,
        {
            "event": "BULK_FILE_INGESTED",
            "imported": imported,
            "completed": completed
        }
    )
    return {"status": "success", "total_imported": imported, "ready_for_assignment": completed}


@router.put("/{lead_id}/assign", status_code=status.HTTP_200_OK)
async def assign_sales_lead(
    lead_id: int,
    payload: LeadAssignRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    actor_id = await _extract_user_id(current_user, db)
    actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "Admin")

    # If no sales_rep_id supplied, assign to the logged-in Admin
    target_user_id = payload.sales_rep_id if payload.sales_rep_id else actor_id
    stmt_user = select(User).filter(User.id == target_user_id)
    res_user = await db.execute(stmt_user)
    target_user = res_user.scalars().first()
    target_name = getattr(target_user, "full_name", None) or getattr(target_user, "email", actor_name) if target_user else actor_name

    lead.assigned_to_id = target_user_id
    lead.assigned_at = datetime.utcnow()
    await db.commit()

    activity = CRMLeadActivity(
        lead_id=lead_id,
        performed_by_id=actor_id,
        department="SALES",
        action_type="ASSIGNMENT",
        previous_stage=lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage),
        new_stage=lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage),
        description=f"Assigned to {target_name}"
    )
    db.add(activity)

    notif = CRMNotification(
        recipient_id=target_user_id,
        sender_id=actor_id,
        lead_id=lead_id,
        title="🎯 Lead Assigned",
        message=f"Lead: {lead.lead_name} ({lead.city}). Stops: {lead.number_of_stops or 'N/A'}.",
        notification_type="ASSIGNMENT",
        is_urgent=True
    )
    db.add(notif)
    await db.commit()

    background_tasks.add_task(
        crm_ws_manager.send_to_user,
        target_user_id,
        {
            "event": "LEAD_ASSIGNED_POPUP",
            "lead_id": lead_id,
            "lead_code": lead.lead_code,
            "lead_name": lead.lead_name,
            "city": lead.city,
            "assigned_by": actor_name
        }
    )
    return {"status": "success", "assigned_to": target_name}


@router.post("/{lead_id}/activity", status_code=status.HTTP_200_OK)
async def log_sales_followup(
    lead_id: int,
    payload: LeadStageUpdateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_id = await _extract_user_id(current_user, db)
    lead_name = lead.lead_name
    created_by_id = lead.created_by_id
    prev_stage = lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage)

    lead.stage = payload.new_stage
    if payload.deal_value is not None:
        lead.deal_value = payload.deal_value

    if payload.next_followup_date:
        lead.next_followup_date = payload.next_followup_date
        lead.reminder_note = payload.activity_remarks

    await db.commit()

    activity = CRMLeadActivity(
        lead_id=lead_id,
        performed_by_id=user_id,
        action_type="STAGE_UPDATE",
        description=payload.activity_remarks,
        previous_stage=prev_stage,
        new_stage=payload.new_stage.value,
        department="SALES"
    )
    db.add(activity)

    actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "Admin")

    if payload.new_stage == LeadStageEnum.SALE_DONE:
        notif = CRMNotification(
            recipient_id=None,
            sender_id=user_id,
            lead_id=lead_id,
            title="🏆 SALE DONE - DEAL CLOSED!",
            message=f"{actor_name} marked {lead_name} as SALE DONE! Value: ₹{payload.deal_value or 0.0}.",
            notification_type="SALE_WON",
            is_urgent=True
        )
        db.add(notif)
        await db.commit()

        background_tasks.add_task(
            crm_ws_manager.broadcast_to_admins,
            {
                "event": "SALE_DONE_ALERT",
                "title": "🏆 SALE DONE!",
                "lead_id": lead_id,
                "lead_name": lead_name,
                "sales_rep": actor_name,
                "deal_value": float(payload.deal_value or 0.0),
                "sound": "victory_bell"
            }
        )
    else:
        notif = CRMNotification(
            recipient_id=created_by_id,
            sender_id=user_id,
            lead_id=lead_id,
            title=f"Lead Update: {lead_name}",
            message=f"Stage: '{payload.new_stage.value}'. Remarks: {payload.activity_remarks}",
            notification_type="STAGE_UPDATE"
        )
        db.add(notif)
        await db.commit()

        background_tasks.add_task(
            crm_ws_manager.broadcast_to_admins,
            {
                "event": "STAGE_UPDATED",
                "lead_id": lead_id,
                "lead_name": lead_name,
                "new_stage": payload.new_stage.value,
                "remarks": payload.activity_remarks
            }
        )

    return {"status": "success", "stage": payload.new_stage.value}


# ==================== DEPARTMENT HANDOFFS (ADMIN-FIRST) ====================

@router.post("/{lead_id}/handoff/finance", status_code=status.HTTP_200_OK)
async def handoff_to_finance(
    lead_id: int,
    payload: FinanceHandoffRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_id = await _extract_user_id(current_user, db)
    officer_id = payload.finance_officer_id if payload.finance_officer_id else user_id

    lead.current_department = DepartmentWorkflowEnum.FINANCE
    lead.deal_value = payload.deal_value
    lead.advance_payment_received = payload.advance_payment_received
    lead.finance_approved_by_id = officer_id
    lead.finance_notes = payload.remarks
    await db.commit()

    activity = CRMLeadActivity(
        lead_id=lead_id,
        performed_by_id=user_id,
        action_type="FINANCE_HANDOFF",
        description=f"Routed to Finance. Value: ₹{payload.deal_value}, Advance: {payload.advance_payment_received}",
        department="FINANCE"
    )
    db.add(activity)
    await db.commit()

    background_tasks.add_task(
        crm_ws_manager.send_to_user,
        officer_id,
        {
            "event": "FINANCE_QUEUE_ALERT",
            "lead_id": lead_id,
            "lead_name": lead.lead_name,
            "deal_value": payload.deal_value
        }
    )
    return {"status": "success", "department": DepartmentWorkflowEnum.FINANCE.value}


@router.post("/{lead_id}/operation", status_code=status.HTTP_200_OK)
@router.post("/{lead_id}/handoff/operation", status_code=status.HTTP_200_OK)
async def handoff_to_operation(
    lead_id: int,
    payload: OperationHandoffRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_id = await _extract_user_id(current_user, db)
    incharge_id = payload.operation_incharge_id if payload.operation_incharge_id else user_id

    lead.current_department = DepartmentWorkflowEnum.OPERATION
    lead.operation_assigned_to_id = incharge_id
    lead.site_ready_for_installation = payload.site_ready_for_installation
    lead.operation_notes = payload.remarks
    await db.commit()

    activity = CRMLeadActivity(
        lead_id=lead_id,
        performed_by_id=user_id,
        action_type="OPERATION_HANDOFF",
        description=f"Site Ready: {payload.site_ready_for_installation}. Remarks: {payload.remarks}",
        department="OPERATION"
    )
    db.add(activity)
    await db.commit()

    background_tasks.add_task(
        crm_ws_manager.send_to_user,
        incharge_id,
        {
            "event": "OPERATION_INSTALL_ALERT",
            "lead_id": lead_id,
            "lead_name": lead.lead_name
        }
    )
    return {"status": "success", "department": DepartmentWorkflowEnum.OPERATION.value}


@router.post("/{lead_id}/handoff/service", status_code=status.HTTP_200_OK)
async def handoff_to_service(
    lead_id: int,
    payload: ServiceHandoffRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_id = await _extract_user_id(current_user, db)
    service_id = payload.service_incharge_id if payload.service_incharge_id else user_id

    lead.current_department = DepartmentWorkflowEnum.SERVICE
    lead.service_incharge_id = service_id
    lead.assigned_contractor_name = payload.assigned_contractor_name
    lead.assigned_technician_name = payload.assigned_technician_name
    lead.service_notes = payload.remarks
    await db.commit()

    activity = CRMLeadActivity(
        lead_id=lead_id,
        performed_by_id=user_id,
        action_type="SERVICE_HANDOFF",
        description=f"Contractor: {payload.assigned_contractor_name}, Tech: {payload.assigned_technician_name}",
        department="SERVICE"
    )
    db.add(activity)
    await db.commit()

    background_tasks.add_task(
        crm_ws_manager.send_to_user,
        service_id,
        {
            "event": "SERVICE_COMMISSION_ALERT",
            "lead_id": lead_id,
            "contractor": payload.assigned_contractor_name
        }
    )
    return {"status": "success", "department": DepartmentWorkflowEnum.SERVICE.value}


# ==================== FINAL COMMISSIONING & AMC HANDOVER ====================

@router.post("/{lead_id}/commissioning/complete", status_code=status.HTTP_200_OK)
async def complete_lead_commissioning(
    lead_id: int,
    payload: ServiceCommissioningCompleteRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_id = await _extract_user_id(current_user, db)
    lead_name = lead.lead_name

    lead.commissioning_completed = True
    lead.current_department = DepartmentWorkflowEnum.COMPLETED
    await db.commit()

    activity = CRMLeadActivity(
        lead_id=lead_id,
        performed_by_id=user_id,
        department="SERVICE",
        action_type="COMMISSIONING_COMPLETE",
        description=f"{payload.remarks} (AMC: {payload.amc_contract_number})",
        new_stage="Handover Completed"
    )
    db.add(activity)

    notif = CRMNotification(
        recipient_id=None,
        sender_id=user_id,
        lead_id=lead_id,
        title="🎉 LIFT COMMISSIONED & HANDED OVER!",
        message=f"{lead_name} has been certified and commissioned under AMC.",
        notification_type="SYSTEM",
        is_urgent=True
    )
    db.add(notif)
    await db.commit()

    background_tasks.add_task(
        crm_ws_manager.broadcast_to_admins,
        {
            "event": "LIFT_COMMISSIONED",
            "title": "🎉 Lift Handover Complete!",
            "lead_id": lead_id,
            "lead_name": lead_name,
            "contractor": lead.assigned_contractor_name
        }
    )
    return {"status": "success", "department": "COMPLETED", "commissioning_completed": True}


# ==================== STEPPER LOGISTICAL TRACKING ====================

@router.get("/{lead_id}/tracker", response_model=LeadTrackerTimelineResponse)
async def get_lead_stepper_tracking(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = (
        select(CRMLead)
        .options(
            selectinload(CRMLead.created_by),
            selectinload(CRMLead.assigned_to),
            selectinload(CRMLead.activities).selectinload(CRMLeadActivity.performed_by)
        )
        .filter(CRMLead.id == lead_id)
    )
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    lead_activities = lead.activities or []
    sorted_activities = sorted(lead_activities, key=lambda x: x.created_at)

    def extract_events(dept: str) -> List[SubMilestoneEvent]:
        events = []
        for a in sorted_activities:
            if getattr(a, "department", "SALES") == dept:
                actor_name = "Admin"
                if a.performed_by:
                    actor_name = getattr(a.performed_by, "full_name", None) or getattr(a.performed_by, "email", "Admin")
                events.append(
                    SubMilestoneEvent(
                        title=a.action_type.replace("_", " ").title() if a.action_type else "Activity",
                        description=a.description,
                        timestamp=a.created_at,
                        performed_by=actor_name,
                        department=a.department
                    )
                )
        return events

    dept_hierarchy = ["SALES", "FINANCE", "OPERATION", "SERVICE", "COMPLETED"]
    cur_val = lead.current_department.value if hasattr(lead.current_department, "value") else str(lead.current_department)
    curr_dept_idx = dept_hierarchy.index(cur_val) if cur_val in dept_hierarchy else 0

    def calc_status(stage_idx: int) -> str:
        if curr_dept_idx > stage_idx:
            return "COMPLETED"
        elif curr_dept_idx == stage_idx:
            return "IN_PROGRESS"
        return "PENDING"

    creator_name = "Admin"
    if lead.created_by:
        creator_name = getattr(lead.created_by, "full_name", None) or getattr(lead.created_by, "email", "Admin")

    source_val = lead.source.value if hasattr(lead.source, "value") else str(lead.source)
    ingest_events = [
        SubMilestoneEvent(
            title="Lead Ingested",
            description=f"Source: {source_val}. Specs Provided: {lead.is_completed_data}",
            timestamp=lead.created_at,
            performed_by=creator_name,
            department="SALES"
        )
    ]
    if lead.assigned_to:
        assignee_name = getattr(lead.assigned_to, "full_name", None) or getattr(lead.assigned_to, "email", "Admin")
        ingest_events.append(
            SubMilestoneEvent(
                title="Lead Assigned",
                description=f"Assigned to {assignee_name}",
                timestamp=lead.assigned_at or lead.created_at,
                performed_by="Admin",
                department="SALES"
            )
        )

    sales_events = [e for e in extract_events("SALES") if e.title.upper() != "CREATION"]
    finance_events = extract_events("FINANCE")
    if lead.advance_payment_received and not any("Advance" in (e.description or "") for e in finance_events):
        finance_events.append(
            SubMilestoneEvent(
                title="Advance Payment Received",
                description=f"Advance confirmed. Contract: ₹{lead.deal_value or 0}",
                timestamp=lead.updated_at,
                performed_by="Admin",
                department="FINANCE"
            )
        )

    op_events = extract_events("OPERATION")
    service_events = extract_events("SERVICE")

    is_sale_done = (lead.stage == LeadStageEnum.SALE_DONE) or (curr_dept_idx > 0)
    is_fully_commissioned = bool(lead.commissioning_completed or cur_val == "COMPLETED")

    milestones = [
        MainMilestoneStep(
            step_key="INGESTION",
            title="Lead Confirmed & Assigned",
            status="COMPLETED",
            completed_at=lead.created_at,
            sub_events=ingest_events
        ),
        MainMilestoneStep(
            step_key="SALES",
            title=f"Sales Pipeline ({lead.stage.value if hasattr(lead.stage, 'value') else lead.stage})",
            status="COMPLETED" if is_sale_done else "IN_PROGRESS",
            completed_at=sales_events[-1].timestamp if sales_events and is_sale_done else None,
            sub_events=sales_events
        ),
        MainMilestoneStep(
            step_key="FINANCE",
            title="Finance Approval & Advance Cleared",
            status=calc_status(1),
            completed_at=finance_events[-1].timestamp if finance_events and curr_dept_idx > 1 else None,
            sub_events=finance_events
        ),
        MainMilestoneStep(
            step_key="OPERATION",
            title="Shaft Inspection & Installation Dispatch",
            status=calc_status(2),
            completed_at=op_events[-1].timestamp if op_events and curr_dept_idx > 2 else None,
            sub_events=op_events
        ),
        MainMilestoneStep(
            step_key="SERVICE",
            title="Field Technician Commissioning & AMC Handover",
            status="COMPLETED" if is_fully_commissioned else calc_status(3),
            completed_at=service_events[-1].timestamp if service_events and is_fully_commissioned else None,
            sub_events=service_events
        )
    ]

    return LeadTrackerTimelineResponse(
        lead_id=lead.id,
        lead_code=lead.lead_code,
        lead_name=lead.lead_name,
        city=lead.city,
        current_department=cur_val,
        overall_stage=lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage),
        deal_value=float(lead.deal_value) if lead.deal_value is not None else None,
        advance_payment_received=bool(lead.advance_payment_received),
        site_ready_for_installation=bool(lead.site_ready_for_installation),
        assigned_contractor_name=lead.assigned_contractor_name,
        assigned_technician_name=lead.assigned_technician_name,
        lift_specifications={
            "stops": str(lead.number_of_stops or "N/A"),
            "capacity": str(lead.passenger_capacity or "N/A"),
            "shaft": f"{lead.shaft_width or 'N/A'} x {lead.shaft_depth or 'N/A'}",
            "pit": str(lead.pit_height or "N/A")
        },
        milestones=milestones
    )


# ==================== CLEAN PROPOSAL: EDIT, DOWNLOAD & 100% DYNAMIC SHARE ====================

@router.get("/{lead_id}/proposal", status_code=status.HTTP_200_OK)
async def get_lead_proposal(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return _build_lead_proposal_dict(lead)


@router.put("/{lead_id}/proposal", status_code=status.HTTP_200_OK)
async def update_lead_proposal(
    lead_id: int,
    payload: ProposalUpdatePayload = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    if payload.cost_per_lift is not None:
        lead.deal_value = payload.cost_per_lift
    if payload.customer_name:
        lead.lead_name = payload.customer_name.strip()
    if payload.site_address:
        lead.address = payload.site_address.strip()
    if payload.car_travel:
        lead.number_of_stops = payload.car_travel.strip()
    if payload.lift_well:
        parts = payload.lift_well.lower().split("x")
        if len(parts) >= 2:
            lead.shaft_width = parts[0].strip()
            lead.shaft_depth = parts[1].strip()

    await db.commit()
    await db.refresh(lead)

    updated_proposal = _build_lead_proposal_dict(lead)
    if payload.price_in_words:
        updated_proposal["page_5_features_and_pricing"]["price_schedule"]["price_in_words"] = payload.price_in_words
        updated_proposal["price_schedule"]["price_in_words"] = payload.price_in_words

    return {
        "status": "success",
        "message": "Proposal updated successfully",
        "updated_data": updated_proposal
    }


# 1. PUBLIC DOWNLOAD LINK (No Auth Header Required - Direct Browser & WhatsApp)
@router.get("/{lead_id}/proposal/download")
async def download_lead_proposal_pdf(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Proposal not found or expired.")

    proposal_data = _build_lead_proposal_dict(lead)
    pdf_bytes = generate_guidex_9page_pdf(proposal_data)

    filename = f"GUIDEX_Proposal_{lead.lead_code}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf"
        }
    )


# 2. 100% DYNAMIC SHARE ENDPOINT
@router.post("/{lead_id}/proposal/share", status_code=status.HTTP_200_OK)
async def share_lead_proposal(
    lead_id: int,
    request: Request,
    payload: ProposalShareRequest = Body(default_factory=ProposalShareRequest),
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).filter(CRMLead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    user_id = await _extract_user_id(current_user, db)
    sender_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "Admin")

    # Dynamic values extracted directly from the target lead
    client_name = (payload.client_name or lead.lead_name or "Valued Client").strip()
    target_phone = (payload.client_phone or lead.lead_number or "").strip()
    location_str = f"{lead.address or ''}, {lead.city or ''}".strip(", ") or "Odisha"
    travel_str = lead.number_of_stops or "G+3"
    deal_amt = float(lead.deal_value) if lead.deal_value else 913700.00

    # Dynamic full URL (Accessible by any browser/phone without token)
    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/api/crm/leads/{lead.id}/proposal/download"

    # Clean formatted message
    share_text = (
        f"Hello {client_name},\n\n"
        f"Here is your official 9-page GUIDEX Elevator Commercial & Technical Proposal.\n\n"
        f"* Project / Client: {client_name}\n"
        f"* Site Location: {location_str}\n"
        f"* Travel / Stops: {travel_str}\n"
        f"* Contract Value: INR {deal_amt:,.2f}\n\n"
        f"Download PDF Proposal:\n{download_url}\n\n"
        f"Best regards,\nGUIDEX ELEVATOR PVT. LTD.\nPh: +91 9668654365"
    )

    clean_phone = "".join(filter(str.isdigit, target_phone))
    encoded_text = urllib.parse.quote(share_text)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}" if clean_phone else f"https://api.whatsapp.com/send?text={encoded_text}"

    # Record activity in CRM
    activity = CRMLeadActivity(
        lead_id=lead.id,
        performed_by_id=user_id,
        department="SALES",
        action_type="PROPOSAL_SHARED",
        description=f"9-page Proposal shared dynamically with {client_name} ({target_phone or 'No Phone'}) via {payload.share_channel or 'WHATSAPP'}",
        previous_stage=lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage),
        new_stage=lead.stage.value if hasattr(lead.stage, "value") else str(lead.stage)
    )
    db.add(activity)

    notif = CRMNotification(
        recipient_id=None,
        sender_id=user_id,
        lead_id=lead.id,
        title="Proposal Shared",
        message=f"Proposal for {client_name} generated and shared by {sender_name}.",
        notification_type="SYSTEM"
    )
    db.add(notif)
    await db.commit()

    return {
        "status": "success",
        "lead_id": lead.id,
        "lead_code": lead.lead_code,
        "client_name": client_name,
        "phone": target_phone,
        "download_url": download_url,
        "whatsapp_share_url": whatsapp_url,
        "share_message": share_text
    }


# ==================== EXECUTIVE DASHBOARD ANALYTICS ====================

@router.get("/analytics/dashboard", response_model=ExecutiveDashboardAnalytics)
async def get_executive_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    repo = CRMLeadRepository(db)
    return await repo.get_analytics()


# ==================== QUERY & BROADCAST ====================

@router.get("", response_model=List[LeadDetailOut])
async def get_leads(
    department: Optional[DepartmentWorkflowEnum] = None,
    stage: Optional[LeadStageEnum] = None,
    priority: Optional[LeadPriorityEnum] = None,
    assigned_to_me: bool = False,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = select(CRMLead).options(
        selectinload(CRMLead.created_by),
        selectinload(CRMLead.assigned_to),
        selectinload(CRMLead.activities).selectinload(CRMLeadActivity.performed_by)
    )

    if assigned_to_me:
        user_id = await _extract_user_id(current_user, db)
        stmt = stmt.filter(CRMLead.assigned_to_id == user_id)
    if department:
        stmt = stmt.filter(CRMLead.current_department == department)
    if stage:
        stmt = stmt.filter(CRMLead.stage == stage)
    if priority:
        stmt = stmt.filter(CRMLead.priority == priority)
    if search:
        search_filter = f"%{search}%"
        stmt = stmt.filter(
            or_(
                CRMLead.lead_name.ilike(search_filter),
                CRMLead.lead_number.ilike(search_filter),
                CRMLead.lead_code.ilike(search_filter)
            )
        )

    stmt = stmt.order_by(CRMLead.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadDetailOut)
async def get_lead_details_and_full_history(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    stmt = (
        select(CRMLead)
        .options(
            selectinload(CRMLead.created_by),
            selectinload(CRMLead.assigned_to),
            selectinload(CRMLead.activities).selectinload(CRMLeadActivity.performed_by)
        )
        .filter(CRMLead.id == lead_id)
    )
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return lead


@router.post("/announcements", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
async def broadcast_announcement(
    payload: AnnouncementCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    user_id = await _extract_user_id(current_user, db)
    repo = CRMLeadRepository(db)
    notif = await repo.create_notification(
        recipient_id=None,
        sender_id=user_id,
        title=payload.title,
        message=payload.message,
        notification_type="ANNOUNCEMENT",
        is_urgent=payload.is_urgent
    )

    actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "Admin")
    background_tasks.add_task(
        crm_ws_manager.broadcast_announcement,
        {
            "event": "ANNOUNCEMENT_POPUP",
            "title": payload.title,
            "message": payload.message,
            "sender": actor_name,
            "is_urgent": payload.is_urgent
        }
    )
    return notif


@router.get("/notifications", response_model=List[NotificationOut])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    user_id = await _extract_user_id(current_user, db)
    stmt = (
        select(CRMNotification)
        .options(
            selectinload(CRMNotification.sender),
            selectinload(CRMNotification.recipient)
        )
        .filter(
            or_(
                CRMNotification.recipient_id == user_id,
                CRMNotification.recipient_id.is_(None)
            )
        )
        .order_by(CRMNotification.created_at.desc())
        .limit(50)
    )
    res = await db.execute(stmt)
    return res.scalars().all()