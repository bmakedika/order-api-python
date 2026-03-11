from sqlalchemy.orm import Session
from uuid import UUID
from app.models.product import ProductModel

def get_all(db: Session) -> list[ProductModel]:
    return db.query(ProductModel).filter(
        ProductModel.is_active == True
        ).all()


def get_by_id(db: Session, product_id: UUID) -> ProductModel | None:
    return db.query(ProductModel).filter(
        ProductModel.id == product_id,
        ProductModel.is_active == True
        ).first()
        
        
def create(db: Session, data: dict) -> ProductModel:
        product = ProductModel(**data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product


def update(db: Session, product: ProductModel, data: dict) -> ProductModel:
    for key, value in data.items():
         setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def soft_delete(db: Session, product: ProductModel) -> None:
    product.is_active = False
    db.commit()