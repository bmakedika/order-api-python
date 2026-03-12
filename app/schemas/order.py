from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List
from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    customer_id: str
    currency: str


class OrderItemAdd(BaseModel):
    product_id: UUID
    quantity: int


class OrderItemResponse(BaseModel):
    id : UUID
    product_id: UUID
    quantity : int
    unit_price_cents: int
    line_total_cents: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    total_cents: int
    currency: str
    customer_id: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
