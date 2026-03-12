from sqlalchemy.orm import Session
from uuid import UUID
from app.models.order import OrderModel, OrderItemModel



def create(db: Session, data: dict) -> OrderModel:
    order = OrderModel(**data)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order



def get_by_id(db: Session, order_id: UUID) -> OrderModel | None:
    return db.query(OrderModel).filter(OrderModel.id == order_id).first()



def add_item(db: Session, data: dict) -> OrderItemModel:
    item = OrderItemModel(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item



def remove_item(db: Session, order_id: UUID, item_id: UUID) -> bool:
    item = db.query(OrderItemModel).filter(
        OrderItemModel.id == item_id,
        OrderItemModel.order.id == order_id,
    ).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True



def update_total(db: Session, order: OrderModel) -> OrderModel:
    order.total_cents = sum(item.line_total_cents for item in order.items)
    db.commit()
    db.refresh(order)
    return order