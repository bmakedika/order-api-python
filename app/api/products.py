from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import Optional
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductList
from app.core.auth import require_admin
from app.core.database import get_db
from app.services import product_service
from sqlalchemy.orm import Session
from app.core.audit import performance_audit


router = APIRouter()


@router.get('/products', response_model=ProductList)
def get_products(
    page: int = 1,
    page_size: int = 10,
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db),
):
    
    return product_service.list_products(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )


@router.get('/products/{id}', response_model=Product)
def get_product(id: UUID, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


@router.post('/products', response_model=Product)
def create_product(
    product: ProductCreate,
    _=Depends(require_admin),
    db: Session = Depends(get_db),
):
    return product_service.create_product(db, product)


@router.patch('/products/{id}', response_model=Product)
def update_product(
    id: UUID, 
    update: ProductUpdate, 
    _= Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = product_service.update_product(db, id, update)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


@router.delete('/products/{id}', status_code=204)
def delete_product(
    id: UUID,
    _=Depends(require_admin),
    db: Session = Depends(get_db),
):
    deleted = product_service.delete_product(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Product not found')