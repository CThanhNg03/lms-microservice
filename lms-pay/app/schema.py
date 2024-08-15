from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.model.invoice import InvoiceStatus

class NewPaymentInfo(BaseModel):
    card_holder: str
    card_number: str
    cvv: str
    exp_date: str
    billing_address: str

class NewInvoice(BaseModel):
    client_id: int
    raise_date: datetime = Field(default_factory=datetime.now)
    summary: str
    payment_method: str
    payment_info: Optional[NewPaymentInfo] = None

class NewInvoiceItem(BaseModel):
    course_id: int
    amount: int
    author_id: int

class InvoiceUpdate(BaseModel):
    invoice_id: int
    status: InvoiceStatus

class NewOrder(NewInvoice):
    items: List[NewInvoiceItem]

class PaymentResult(BaseModel):
    status: str
    message: str
    data: dict

class ReportRequest(BaseModel):
    start_date: str
    end_date: str
    author_id: int
    course_id: List[int] = []