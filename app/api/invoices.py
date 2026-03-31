from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.auth import require_user, require_admin
from app.core.database import get_db
from app.models.invoice import InvoiceModel as Invoice
from app.schemas.invoice import InvoiceResponse
from app.core.audit import performance_audit

router = APIRouter()


@router.get('/invoices/{invoice_id}', response_model=InvoiceResponse)
@performance_audit
def get_invoice(
    invoice_id: UUID, 
    _= Depends(require_user),
    db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get('/orders/{order_id}/invoices', response_model=List[InvoiceResponse])
@performance_audit
def get_invoices_by_order(
    order_id: UUID, 
    _= Depends(require_user),
    db: Session = Depends(get_db)):
    invoices = db.query(Invoice).filter(Invoice.id_order == order_id).all()
    return invoices