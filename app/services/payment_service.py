from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from app.repos import order_repo
from app.models.order import OrderStatus
from app.core.redis_client import get_redis
from app.services.invoice_service import create_invoice


IDEMPOTENCY_TTL = 86400

def pay_order(db: Session, order_id: UUID, idempotency_key: str):
    redis = get_redis()
    
    cached = redis.get(f'idempotency:{idempotency_key}')
    if cached:
        return order_repo.get_by_id(db, order_id), 'already_processed'

    order = order_repo.get_by_id(db, order_id)
    if not order:
        return None, 'order_not_found'
    
    if order.status != OrderStatus.DRAFT:
        return order, 'invalid_status'

    if order.total_cents == 0:
        return order, 'empty_order'
    
    order.status = OrderStatus.PAID
    db.commit()
    db.refresh(order)
    
    create_invoice(db, order, id_payment=uuid4())

    redis.set(f'idempotency:{idempotency_key}', 'paid', ex=IDEMPOTENCY_TTL)

    return order, None