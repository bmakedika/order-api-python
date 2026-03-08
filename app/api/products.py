from fastapi import FastAPI, HTTPException, Depends
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.storage.fake_db import products
from dependencies.auth import require_admin




app = FastAPI()

# Endpoints

@app.get("/products/{id}", response_model=Product)
def get_product(id: UUID):
    for product in products:
        if product.id == id:
            return product
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
    for product in products:
        if product.id == id:
            found = product
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