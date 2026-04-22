from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.repos import order_repo, product_repo
from app.schemas.order import OrderCreate, OrderItemAdd
from app.models.order import OrderStatus


def create_order(db: Session, data: OrderCreate):
    return order_repo.create(db, {
        'id': uuid4(),
        'customer_id': data.customer_id,
        'currency': data.currency,
        'status': OrderStatus.DRAFT,
        'total_cents': 0,
        'created_at': datetime.now(timezone.utc),
    })



def get_order(db: Session, order_id: UUID):
    return order_repo.get_by_id(db, order_id)


def add_item(db: Session, order_id: UUID, data: OrderItemAdd):
    order = order_repo.get_by_id(db, order_id)
    if not order:
        return None, 'order not found'
    
    if order.status != OrderStatus.DRAFT:
        return None, 'cannot modify a non-draft order'
    
    product = product_repo.get_by_id(db, data.product_id)
    if not product or not product.is_active:
        return None, 'product not available'
    
    if data.quantity <= 0:
        return None, 'invalid quantity'
    
    existing_item = order_repo.get_item_by_product(db, order_id, data.product_id)

    if existing_item:
        existing_item.quantity += data.quantity
        existing_item.line_total_cents = existing_item.quantity * existing_item.unit_price_cents
        order_repo.save(db, existing_item)

        item = existing_item

    else:
        line_total_cents = product.price_cents * data.quantity

        item = order_repo.add_item(db, {
            'id': uuid4(),
            'order_id': order_id,
            'product_id': data.product_id,
            'quantity': data.quantity,
            'unit_price_cents': product.price_cents,
            'line_total_cents': line_total_cents,
        })
    
    order.total_cents = sum(i.line_total_cents for i in order.items)
    order_repo.save(db, order)

    return item, None



def remove_item(db: Session, order_id: UUID, item_id: UUID):
    order = order_repo.get_by_id(db, order_id)
    if not order:
        return None, 'order not found'
    
    if order.status != OrderStatus.DRAFT:
        return None, 'cannot modify a non-draft order'
    
    deleted = order_repo.remove_item(db, order_id, item_id)
    if not deleted:
        return None, 'item not found'
    
    order.total_cents = sum(i.line_total_cents for i in order.items)
    order_repo.save(db, order)
    return True, None