from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class ProductModel(Base):
    __tablename__ = "products"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price_cents = Column(Integer, nullable=False)
    currency    = Column(String, nullable=False, default='EUR')
    category    = Column(String, nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))