from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductList
from app.storage.fake_db import products
from app.core.auth import require_admin
from app.services.product_service import get_product_by_id, list_products as list_products_service


router = APIRouter()


@router.get('/products', response_model=ProductList)
def get_products(
    page: int = 1,
    page_size: int = 10,
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: Optional[str] = None,
):
    
    return list_products_service(
        page=page,
        page_size=page_size,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )


@router.get('/products/{id}', response_model=Product)
def get_product(id: UUID):
    product = get_product_by_id(id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


@router.post(
    '/products',
    response_model=Product,
    responses={
        401: {'description': 'Missing or invalid API Key'},
        403: {'description': 'Forbidden - admin only'}
    },
)
def create_product(product: ProductCreate, _ = Depends(require_admin)):
    new_product = Product(
        id=uuid4(),
        name=product.name,
        description=product.description,
        price_cents=product.price_cents,
        currency=product.currency,
        category=product.category,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    products.append(new_product)
    return new_product


@router.patch(
    '/products/{id}',
    response_model=Product,
    responses={
        401: {'description': 'Missing or invalid token'},
        403: {'description': 'Forbidden - admin only'},
        404: {'description': 'Product not found'},
    },
)
def update_product(id: UUID, update: ProductUpdate, _ = Depends(require_admin)):
    for product in products:
        if product.id == id:
            found = product
            break
    else:
        raise HTTPException(status_code=404, detail='Product not found')

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


@router.delete(
    '/products/{id}',
    status_code=204,
    responses={
        401: {"description": "Missing or invalid token"},
        403: {"description": "Forbidden - admin only"},
        404: {"description": "Product not found"},
    },
)
def delete_product(id: UUID, _ = Depends(require_admin)):
    for product in products:
        if product.id == id:
            found = product
            break
    else:
        raise HTTPException(status_code=404, detail='Product not found')

    found.is_active = False