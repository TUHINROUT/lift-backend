from celery import Celery
from celery.schedules import crontab


celery_app = Celery(
    "lift_backend",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

# Import task modules so Celery registers all tasks.
celery_app.conf.imports = (
    "app.modules.attendance.tasks",
)

celery_app.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,

    beat_schedule={
        "auto-punch-out-at-midnight": {
            "task": (
                "app.modules.attendance.tasks."
                "auto_punch_out_open_attendance"
            ),
            "schedule": crontab(
                hour=0,
                minute=0,
            ),
        },
    },
)