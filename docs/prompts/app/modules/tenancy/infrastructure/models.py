"""tenancy infrastructure models — SQLAlchemy models."""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class TenantModel(BaseModel):
    """TenantModel — โมเดล tenants (schema: public)."""
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = Column(String(36), primary_key=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    plan = Column(String(20), nullable=False, default="FREE")
    status = Column(String(20), nullable=False, default="ACTIVE")
    schema_name = Column(String(100), unique=True, nullable=False)
    owner_email = Column(String(255), nullable=False)
    trial_ends_at = Column(DateTime(timezone=True))
    max_users = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=1)