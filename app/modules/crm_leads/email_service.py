import os
import smtplib
import ssl
import asyncio
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# Port 465 (Direct SSL) bypasses ISP port 587 STARTTLS blocking
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = os.getenv("SMTP_USER") or os.getenv("EMAIL_HOST_USER", "somniates@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_HOST_PASSWORD", "egfzbaviembqjvla").strip()
SMTP_FROM_NAME = "GUIDEX ELEVATOR PVT. LTD."


def _send_email_sync(to_email: str, subject: str, body_text: str, pdf_bytes: bytes, pdf_filename: str) -> bool:
    message = EmailMessage()
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body_text)

    # Attach the 9-page PDF
    message.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=pdf_filename
    )

    try:
        print(f"[SMTP CONNECTING] Connecting via SSL to {SMTP_HOST}:{SMTP_PORT} as {SMTP_USER}...")
        ssl_ctx = ssl.create_default_context()

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl_ctx, timeout=30) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)

        print(f"[SMTP DELIVERED] Successfully dispatched email to {to_email} via Port 465!")
        return True
    except Exception as exc:
        print(f"[SMTP ERROR] Failed to dispatch via Port 465: {exc}")
        return False


async def send_proposal_pdf_email(
    to_email: str,
    subject: str,
    body_text: str,
    pdf_bytes: bytes,
    pdf_filename: str
) -> bool:
    return await asyncio.to_thread(
        _send_email_sync,
        to_email,
        subject,
        body_text,
        pdf_bytes,
        pdf_filename
    )