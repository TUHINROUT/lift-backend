from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
)

from app.modules.reports.schemas import LiftReportResponse


# =================================
# PATHS
# =================================

BASE_UPLOAD_DIR = Path("uploads")


# =================================
# IMAGE HELPER (TASK ATTACHMENTS)
# =================================

def get_uploaded_file_path(
    relative_path: str | None,
) -> Path | None:
    if not relative_path:
        return None

    file_path = BASE_UPLOAD_DIR / relative_path

    if not file_path.exists():
        return None

    return file_path


# =================================
# DATE FORMATTER
# =================================

def format_datetime(
    value: datetime | None,
) -> str:
    if value is None:
        return "Not Available"

    return value.strftime(
        "%d %b %Y, %I:%M %p"
    )


# =================================
# PDF HEADER / FOOTER
# =================================

def draw_page_header_footer(
    canvas,
    document,
):
    canvas.saveState()

    page_width, page_height = A4

    # ---------------------------------
    # Header line
    # ---------------------------------
    canvas.setStrokeColor(
        colors.HexColor("#D9D9D9")
    )
    canvas.setLineWidth(0.5)

    canvas.line(
        15 * mm,
        page_height - 12 * mm,
        page_width - 15 * mm,
        page_height - 12 * mm,
    )

    # ---------------------------------
    # Header text
    # ---------------------------------
    canvas.setFont(
        "Helvetica-Bold",
        7.5,
    )
    canvas.setFillColor(
        colors.HexColor("#DF173C")
    )
    canvas.drawString(
        15 * mm,
        page_height - 9 * mm,
        "JAGUAR ELEVATORS",
    )

    canvas.setFont(
        "Helvetica",
        7,
    )
    canvas.setFillColor(
        colors.HexColor("#666666")
    )
    canvas.drawRightString(
        page_width - 15 * mm,
        page_height - 9 * mm,
        "Lift Service Report",
    )

    # ---------------------------------
    # Footer line
    # ---------------------------------
    canvas.line(
        15 * mm,
        12 * mm,
        page_width - 15 * mm,
        12 * mm,
    )

    canvas.setFont(
        "Helvetica",
        7,
    )
    canvas.drawString(
        15 * mm,
        7 * mm,
        "Lift Service & Workforce Management System",
    )

    canvas.drawRightString(
        page_width - 15 * mm,
        7 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


# =================================
# MAIN PDF GENERATOR
# =================================

def generate_lift_report_pdf(
    report: LiftReportResponse,
    output_path: str | Path,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="Lift Service Report",
        author="Jaguar Elevators - Workforce Management",
    )

    styles = getSampleStyleSheet()

    # =================================
    # STYLES
    # =================================

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=3 * mm,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=8 * mm,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#222222"),
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    )

    subsection_style = ParagraphStyle(
        "SubsectionTitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#333333"),
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
    )

    center_style = ParagraphStyle(
        "Center",
        parent=body_style,
        alignment=TA_CENTER,
    )

    story = []

    # =================================
    # TITLE & SUBTITLE
    # =================================

    story.append(Spacer(1, 4 * mm))

    story.append(
        Paragraph(
            "LIFT SERVICE REPORT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Service and Maintenance Documentation",
            subtitle_style,
        )
    )

    # =================================
    # CUSTOMER & LIFT
    # =================================

    story.append(
        Paragraph(
            "CUSTOMER & LIFT INFORMATION",
            section_style,
        )
    )

    customer_name = getattr(getattr(report, "customer", None), "name", "Not Available")
    customer_code = getattr(getattr(report, "customer", None), "customer_code", "Not Available")
    current_phase = getattr(report, "current_phase", "Not Available")
    if current_phase:
        current_phase = str(current_phase).replace("_", " ")

    customer_data = [
        [
            Paragraph("Customer", heading_style),
            Paragraph(customer_name or "Not Available", body_style),
        ],
        [
            Paragraph("Customer Code", heading_style),
            Paragraph(customer_code or "Not Available", body_style),
        ],
        [
            Paragraph("Lift Code", heading_style),
            Paragraph(report.lift_code, body_style),
        ],
        [
            Paragraph("Current Phase", heading_style),
            Paragraph(current_phase or "Not Available", body_style),
        ],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[45 * mm, 125 * mm],
    )

    customer_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(customer_table)
    story.append(Spacer(1, 4 * mm))

    # =================================
    # PHASE HISTORY
    # =================================

    story.append(
        Paragraph(
            "PHASE HISTORY",
            section_style,
        )
    )

    if report.phase_history:
        phase_data = [
            [
                Paragraph("Phase", heading_style),
                Paragraph("Completed By", heading_style),
                Paragraph("Completed At", heading_style),
            ]
        ]

        for phase in report.phase_history:
            phase_data.append(
                [
                    Paragraph(str(phase.phase_name).replace("_", " "), body_style),
                    Paragraph(phase.completed_by or "Not Available", body_style),
                    Paragraph(format_datetime(phase.completed_at), body_style),
                ]
            )

        phase_table = Table(
            phase_data,
            colWidths=[55 * mm, 55 * mm, 60 * mm],
            repeatRows=1,
        )

        phase_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(phase_table)
    else:
        story.append(
            Paragraph(
                "No phase history available.",
                body_style,
            )
        )

    # =================================
    # TASKS
    # =================================

    story.append(
        Paragraph(
            "TASK DETAILS",
            section_style,
        )
    )

    if report.tasks:
        for task_index, task in enumerate(report.tasks, start=1):
            story.append(
                Paragraph(
                    f"TASK {task_index} — {task.task_number}",
                    subsection_style,
                )
            )

            due_date_str = (
                task.due_date.strftime("%d %b %Y")
                if task.due_date
                else "Not Available"
            )

            task_data = [
                [
                    Paragraph("Task Number", heading_style),
                    Paragraph(task.task_number, body_style),
                    Paragraph("Status", heading_style),
                    Paragraph(task.status, body_style),
                ],
                [
                    Paragraph("Title", heading_style),
                    Paragraph(task.title, body_style),
                    Paragraph("Assigned To", heading_style),
                    Paragraph(task.assigned_to or "Not Available", body_style),
                ],
                [
                    Paragraph("Assigned By", heading_style),
                    Paragraph(task.assigned_by or "Not Available", body_style),
                    Paragraph("Due Date", heading_style),
                    Paragraph(due_date_str, body_style),
                ],
                [
                    Paragraph("Created At", heading_style),
                    Paragraph(format_datetime(task.created_at), body_style),
                    Paragraph("Task ID", heading_style),
                    Paragraph(str(task.task_id), body_style),
                ],
            ]

            task_table = Table(
                task_data,
                colWidths=[30 * mm, 55 * mm, 30 * mm, 55 * mm],
            )

            task_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F2F2F2")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(task_table)

            # =================================
            # EXECUTION
            # =================================

            story.append(
                Paragraph(
                    "Execution Details",
                    subsection_style,
                )
            )

            if task.execution:
                execution = task.execution

                start_loc = (
                    f"{execution.start_latitude}, {execution.start_longitude}"
                    if execution.start_latitude is not None and execution.start_longitude is not None
                    else "Not Available"
                )
                comp_loc = (
                    f"{execution.completed_latitude}, {execution.completed_longitude}"
                    if execution.completed_latitude is not None and execution.completed_longitude is not None
                    else "Not Available"
                )

                execution_data = [
                    [
                        Paragraph("Execution Status", heading_style),
                        Paragraph(execution.status or "Not Available", body_style),
                    ],
                    [
                        Paragraph("Start Time", heading_style),
                        Paragraph(format_datetime(execution.start_time), body_style),
                    ],
                    [
                        Paragraph("Start Location", heading_style),
                        Paragraph(start_loc, body_style),
                    ],
                    [
                        Paragraph("Completed Time", heading_style),
                        Paragraph(format_datetime(execution.completed_time), body_style),
                    ],
                    [
                        Paragraph("Completed Location", heading_style),
                        Paragraph(comp_loc, body_style),
                    ],
                ]

                execution_table = Table(
                    execution_data,
                    colWidths=[45 * mm, 125 * mm],
                )

                execution_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                story.append(execution_table)

                # =================================
                # CLIENT PHOTO & SIGNATURE
                # =================================

                story.append(
                    Paragraph(
                        "CLIENT VERIFICATION",
                        subsection_style,
                    )
                )

                verification_items = []

                # Client Photo
                photo_path = get_uploaded_file_path(execution.client_photo)
                if photo_path:
                    photo = Image(
                        str(photo_path),
                        width=70 * mm,
                        height=55 * mm,
                    )
                    photo.hAlign = "CENTER"
                    verification_items.append(
                        [Paragraph("Client Photo", heading_style), photo]
                    )
                else:
                    verification_items.append(
                        [
                            Paragraph("Client Photo", heading_style),
                            Paragraph("Not Available", body_style),
                        ]
                    )

                # Client Signature
                sig_path = get_uploaded_file_path(execution.client_signature)
                if sig_path:
                    signature = Image(
                        str(sig_path),
                        width=70 * mm,
                        height=30 * mm,
                    )
                    signature.hAlign = "CENTER"
                    verification_items.append(
                        [Paragraph("Client Signature", heading_style), signature]
                    )
                else:
                    verification_items.append(
                        [
                            Paragraph("Client Signature", heading_style),
                            Paragraph("Not Available", body_style),
                        ]
                    )

                verification_table = Table(
                    verification_items,
                    colWidths=[45 * mm, 125 * mm],
                )

                verification_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ]
                    )
                )
                story.append(verification_table)

            else:
                story.append(
                    Paragraph(
                        "No execution recorded for this task.",
                        body_style,
                    )
                )

            # Questions & Answers
            story.append(
                Paragraph(
                    "Questions & Answers",
                    subsection_style,
                )
            )

            if task.questions_and_answers:
                qa_data = [
                    [
                        Paragraph("Question", heading_style),
                        Paragraph("Answer", heading_style),
                    ]
                ]

                for item in task.questions_and_answers:
                    qa_data.append(
                        [
                            Paragraph(item.question, body_style),
                            Paragraph(item.answer or "Not Answered", body_style),
                        ]
                    )

                qa_table = Table(
                    qa_data,
                    colWidths=[85 * mm, 85 * mm],
                    repeatRows=1,
                )

                qa_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                story.append(qa_table)
            else:
                story.append(
                    Paragraph(
                        "No questions or answers available.",
                        body_style,
                    )
                )

            story.append(Spacer(1, 6 * mm))

    else:
        story.append(
            Paragraph(
                "No tasks available.",
                body_style,
            )
        )

    # =================================
    # TICKETS
    # =================================

    story.append(
        Paragraph(
            "TICKETS & COMPLAINTS",
            section_style,
        )
    )

    if report.tickets:
        for ticket_index, ticket in enumerate(report.tickets, start=1):
            story.append(
                Paragraph(
                    f"TICKET {ticket_index} — {ticket.ticket_number}",
                    subsection_style,
                )
            )

            ticket_data = [
                [
                    Paragraph("Ticket Number", heading_style),
                    Paragraph(ticket.ticket_number, body_style),
                ],
                [
                    Paragraph("Type", heading_style),
                    Paragraph(ticket.ticket_type, body_style),
                ],
                [
                    Paragraph("Priority", heading_style),
                    Paragraph(ticket.priority, body_style),
                ],
                [
                    Paragraph("Status", heading_style),
                    Paragraph(ticket.status, body_style),
                ],
                [
                    Paragraph("Complaint", heading_style),
                    Paragraph(ticket.complaint_description, body_style),
                ],
                [
                    Paragraph("Closing Remarks", heading_style),
                    Paragraph(ticket.closing_remarks or "Not Available", body_style),
                ],
                [
                    Paragraph("Created At", heading_style),
                    Paragraph(format_datetime(ticket.created_at), body_style),
                ],
                [
                    Paragraph("Closed At", heading_style),
                    Paragraph(format_datetime(ticket.closed_at), body_style),
                ],
            ]

            ticket_table = Table(
                ticket_data,
                colWidths=[45 * mm, 125 * mm],
            )

            ticket_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(ticket_table)
            story.append(Spacer(1, 5 * mm))
    else:
        story.append(
            Paragraph(
                "No tickets or complaints available.",
                body_style,
            )
        )

    # =================================
    # FINAL REPORT NOTE
    # =================================

    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "End of Lift Service Report",
            center_style,
        )
    )

    # =================================
    # BUILD PDF
    # =================================

    document.build(
        story,
        onFirstPage=draw_page_header_footer,
        onLaterPages=draw_page_header_footer,
    )