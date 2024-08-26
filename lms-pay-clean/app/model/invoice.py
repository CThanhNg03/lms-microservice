from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from re import T
from typing import List, Optional
from uuid import UUID

from app.model.payment_info import CreatePaymentModel, PaymentInfoModel


@dataclass
class InvoiceModel:
    id: str
    client_id: int 
    raise_date: datetime
    updated_at: datetime
    summary: str
    payment_method: str 
    payment_info: int 
    status: Enum

@dataclass
class InvoiceStatus(Enum):
    PENDING = 1
    PAID = 2
    CANCELLED = 3
    
@dataclass
class InvoiceItemModel:
    invoice_id: UUID
    course_id: int
    author_id: int
    amount: float

@dataclass
class GetInvoiceParamsModel:
    page: int = 1
    size: Optional[int] = 10
    client_id: Optional[int] = None

@dataclass
class GetInvoiceItemParamsModel:
    start_date: datetime
    end_date: datetime
    page: int = None
    size: Optional[int] = 10
    author_id: Optional[List[int]] = None
    course_id: Optional[List[int]] = None

@dataclass
class CreateInvoiceModel:
    client_id: int
    summary: str
    payment_method: str
    payment_info: Optional[CreatePaymentModel]
    raise_date: datetime

@dataclass
class CreateInvoiceItemModel:
    course_id: int
    author_id: int
    amount: int

@dataclass
class CreateOrderModel(CreateInvoiceModel):
    items: List[CreateInvoiceItemModel]

@dataclass
class TransactionModel:
    invoice: UUID
    amount: int
    summary: str
    payment_method: str
    payment_info: Optional[PaymentInfoModel]

