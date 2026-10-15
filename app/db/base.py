from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass

# Keep only external models without circular back-references
from app.modules.tracking.models import EmployeeLocation  # noqa: F401