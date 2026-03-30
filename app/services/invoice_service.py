from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone
from app.models.invoice import InvoiceModel

def create_invoice(db: Session, order, id_payment):
    # generate a unique invoice number using uuid4 
    invoice_number = f"INV-{uuid4()}"
    # calculate tax (20% of total) 
    tax = int(order.total_cents * 0.2)
    # create and save InvoiceModel 
    invoice = InvoiceModel(
        id=uuid4(),
        invoice_number=invoice_number,
        id_order=order.id,
        id_payment=id_payment,
        id_customer=order.customer_id,
        total_cents=order.total_cents,
        tax=tax,
        created_at=datetime.now(timezone.utc)
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice