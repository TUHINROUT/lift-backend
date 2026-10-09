import smtplib
from email.message import EmailMessage
from app.core.config import settings


class EmailSendError(Exception):
    pass


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.DEFAULT_FROM_EMAIL
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
        ) as server:

            if settings.EMAIL_USE_TLS:
                server.starttls()

            server.login(
                settings.EMAIL_HOST_USER,
                settings.EMAIL_HOST_PASSWORD,
            )

            server.send_message(message)

    except (smtplib.SMTPException, OSError) as exc:
        raise EmailSendError(
            "Welcome email could not be sent."
        ) from exc