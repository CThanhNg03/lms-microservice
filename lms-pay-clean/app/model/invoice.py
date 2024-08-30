from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from app.model.payment_info import CreatePaymentModel, PaymentInfoModel

# Invoice expiration time (in minutes)
INVOICE_TTL = 60

@dataclass
class InvoiceModel:
    id: UUID
    client_id: int 
    raise_date: datetime
    updated_at: datetime
    client_email: str
    summary: str
    payment_method: str 
    payment_info: int 
    status: Enum

class InvoiceStatus(Enum):
    PENDING = 1
    PAID = 2
    CANCELED = 3
    
@dataclass
class InvoiceItemModel:
    invoice_id: UUID
    course_id: int
    author_id: int
    amount: float
    course_name: str

@dataclass
class GetInvoiceParamsModel:
    client_id: Optional[int]

@dataclass
class GetInvoiceItemParamsModel:
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    author_id: Optional[List[int]] = None
    course_id: Optional[List[int]] = None
    invoice_id: Optional[UUID] = None
    status: Optional[InvoiceStatus] = None

@dataclass
class CreateInvoiceModel:
    client_id: int
    summary: str
    payment_method: str
    payment_info: Optional[CreatePaymentModel]
    raise_date: datetime
    client_email: str

@dataclass
class CreateInvoiceItemModel:
    course_id: int
    author_id: int
    amount: float
    course_name: str

@dataclass
class CreateOrderModel(CreateInvoiceModel):
    items: List[CreateInvoiceItemModel]

@dataclass
class TransactionModel:
    invoice: UUID
    amount: float
    summary: str
    payment_method: str
    payment_info: Optional[PaymentInfoModel]

@dataclass
class InvoiceDetailModel(CreateOrderModel):
    invoice_id: UUID
    total: float
    updated_at: datetime



