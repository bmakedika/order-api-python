import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base



class InvoiceModel(Base):
    __tablename__ = 'invoices'

    id             = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String, nullable=False)
    id_order       = Column(PG_UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    id_payment     = Column(PG_UUID(as_uuid=True), nullable=False)
    id_customer    = Column(String, nullable=False)
    total_cents    = Column(Integer, nullable=False, default=0)
    tax            = Column(Integer, nullable=False)
    created_at     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order    = relationship('OrderModel', back_populates='invoices')
    items    = relationship('InvoiceItemModel', back_populates='invoice')


class InvoiceItemModel(Base):
    __tablename__ = 'invoice_items'

    id               = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id       = Column(PG_UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    product_id       = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    quantity         = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    line_total_cents = Column(Integer, nullable=False)
    created_at       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    invoice = relationship('InvoiceModel', back_populates='items')