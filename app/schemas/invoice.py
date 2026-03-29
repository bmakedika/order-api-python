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
    order_id: UUID
    total_cents: int
    currency: str
    created_at: datetime
    items: List[InvoiceItemResponse] = []