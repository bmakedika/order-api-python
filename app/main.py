from fastapi import FastAPI
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List


app = FastAPI()

products = []

class ProductCreate(BaseModel):
    name: str
    description: str
    price_cents: int
    currency: str
    category: str

class Product(BaseModel):
    id: UUID
    name: str
    description: str
    price_cents: int
    currency: str
    category: str
    is_active: bool = True
    created_at: datetime

@app.get('/')
def home():
    return {'message': 'order api running'}

@app.get('/products', response_model=List[Product])
def list_products(page: int = 1, page_size: int = 10):
    start = (page - 1) * page_size
    end = start + page_size
    return products[start:end]

@app.post('/products', response_model=Product)
def create_product(product: ProductCreate):
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

