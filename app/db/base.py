from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass

# Import models below Base definition to register them for Alembic without circular import
from app.modules.tracking.models import EmployeeLocation