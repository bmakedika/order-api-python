from fastapi import APIRouter, HTTPException, Depends, Header
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_user, require_admin
from app.schemas.order import OrderCreate, OrderItemAdd, OrderResponse, OrderStatusUpdate
from app.services import order_service
from app.core.audit import performance_audit


router = APIRouter()


@router.post('/orders', response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    _= Depends(require_user),
    db: Session = Depends(get_db)
):
    return order_service.create_order(db, data)



@router.get('/orders/{order_id}', response_model=OrderResponse)
def get_order(
    order_id: UUID,
    _= Depends(require_user),
    db: Session = Depends(get_db)
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order



@router.post('/orders/{order_id}/items', response_model=OrderResponse)
def add_item(
    order_id: UUID,
    data: OrderItemAdd,
    _= Depends(require_user),
    db: Session = Depends(get_db)
):
    item, error = order_service.add_item(db, order_id, data)
    if error == 'order_not_found':
        raise HTTPException(status_code=404, detail='Order not found')
    if error == 'product_not_found':
        raise HTTPException(status_code=404, detail='Product not found')
    db.expire_all()
    order = order_service.get_order(db, order_id)
    return order



@router.delete('/orders/{order_id}/items/{item_id}', status_code=200)
def remove_item(
    order_id: UUID,
    item_id: UUID,
    _= Depends(require_user),
    db: Session = Depends(get_db),
):
    deleted, error = order_service.remove_item(db, order_id, item_id)
    if error == 'order_not_found':
        raise HTTPException(status_code=404, detail='Order not found')
    if error == 'item_not_found':
        raise HTTPException(status_code=404, detail='Item not found')



@router.post('/orders/{order_id}/pay', response_model=OrderResponse)
def pay_order(
    order_id: UUID,
    _= Depends(require_user),
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias='Idempotency-Key'),
):
    from app.services import payment_service
    order, error = payment_service.pay_order(db, order_id, idempotency_key)

    if error == 'order_not_found':
        raise HTTPException(status_code=404, detail='Order not found')
    if error == 'invalid_status':
        raise HTTPException(status_code=409, detail='Order already paid or cancelled')
    if error == 'empty_order':
        raise HTTPException(status_code=400, detail='Cannot pay empty order')
    

    return order



@router.patch('/orders/{order_id}/status', response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    status_update: OrderStatusUpdate,
    _= Depends(require_admin),
    db: Session = Depends(get_db)
):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    order.status = status_update.status
    db.commit()
    db.refresh(order)

    return order