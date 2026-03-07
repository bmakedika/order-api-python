import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Optional
from dotenv import load_dotenv


app = FastAPI()

# Configuration

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


products = []

# Schémas Pydantic

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


# Auth

def require_admin(x_api_key: str = Header()):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# Endpoints

@app.get("/")
def home():
    return {"message": "Order API running"}


@app.get("/products", response_model=ProductList)
def list_products(
    page: int = 1,
    page_size: int = 10,
    category: Optional[str] = None
):
    # 1. filtrer
    if category:
        filtered = [p for p in products if p.category == category]
    else:
        filtered = products

    # 2. total après filtre
    total = len(filtered)

    # 3. pagination
    start = (page - 1) * page_size
    end = start + page_size

    return ProductList(
        items=filtered[start:end],
        page=page,
        page_size=page_size,
        total=total
    )


@app.get("/products/{id}", response_model=Product)
def get_product(id: UUID):
    for p in products:
        if p.id == id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=Product)
def create_product(product: ProductCreate, _ = Depends(require_admin)):
    new_product = Product(
        id=uuid4(),
        name=product.name,
        description=product.description,
        price_cents=product.price_cents,
        currency=product.currency,
        category=product.category,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    products.append(new_product)
    return new_product


@app.patch("/products/{id}", response_model=Product)
def update_product(id: UUID, update: ProductUpdate, _ = Depends(require_admin)):
    for p in products:
        if p.id == id:
            found = p
            break
    else:
        raise HTTPException(status_code=404, detail="Product not found")

    if update.name is not None:
        found.name = update.name
    if update.description is not None:
        found.description = update.description
    if update.price_cents is not None:
        found.price_cents = update.price_cents
    if update.currency is not None:
        found.currency = update.currency
    if update.category is not None:
        found.category = update.category

    return found


@app.delete("/products/{id}", status_code=204)
def delete_product(id: UUID, _ = Depends(require_admin)):
    for p in products:
        if p.id == id:
            found = p
            break
    else:
        raise HTTPException(status_code=404, detail="Product not found")

    found.is_active = False