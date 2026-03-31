from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List

class InvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : UUID
    product_id: UUID
    quantity : int
    unit_price_cents: int
    line_total_cents: int

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    invoice_number: str
    id_order: UUID
    id_payment: UUID
    id_customer: str
    total_cents: int
    tax: int
    created_at: datetime
    items: List[InvoiceItemResponse] = []