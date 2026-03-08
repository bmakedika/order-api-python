from fastapi import FastAPI
from uuid import uuid4 
from datetime import datetime, timezone
from app.storage.fake_db import products
from app.schemas.product import ProductList
from typing import Optional


app = FastAPI()





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


