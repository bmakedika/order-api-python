from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class ProductCreate(BaseModel):
    name: str
    description: str
    price_cents: int
    currency: str
    category: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = None
    currency: Optional[str] = None
    category: Optional[str] = None


class Product(BaseModel):
    id: UUID
    name: str
    description: str
    price_cents: int
    currency: str
    category: str
    is_active: bool = True
    created_at: datetime


class ProductList(BaseModel):
    items: List[Product]
    page: int
    page_size: int
    total: int