from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.repositories import orm
from app.repositories.orm.invoice import InvoiceStatus
from app.setting.setting import logger

T = TypeVar("T")

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
    client_email: Optional[str]

class NewInvoiceItem(BaseModel):
    course_id: int
    amount: float
    author_id: int
    course_name: Optional[str] = "Course"

class InvoiceUpdate(BaseModel):
    invoice_id: UUID
    status: InvoiceStatus

class NewOrder(NewInvoice):
    items: List[NewInvoiceItem]

class PaymentResponse(BaseModel):
    status: str
    message: str
    data: dict

class ReportRequest(BaseModel):
    course_id: str | List[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    author_id: Optional[int] = None
    status: Optional[str] = None
    
    def __init__(self, start_date: datetime = None, end_date: datetime = None, author_id: Optional[int] = None, course_id: str = None, status: Optional[str] = None):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.author_id = author_id
        self.course_id = course_id
        if isinstance(course_id, str):
            course_id = course_id.split(',')
            self.course_id = [int(i) for i in course_id]
        self.status = status
        if status:
            try:
                self.status = InvoiceStatus[status.upper()]
            except KeyError:
                raise ValueError("Invalid status")
        

class PaginationResponse(BaseModel, Generic[T]):
    page: int
    limit: int
    skip: int
    total: int
    items: List[T]

class InvoiceResponse(NewInvoice):
    id: UUID
    status: InvoiceStatus | str
    payment_info: Optional[int] = None

    @field_validator('status', mode='before')
    def serialize_status(cls, v):
        if isinstance(v, InvoiceStatus):
            return v.name
        return v

    class Config:
        from_attributes = True
        use_enum_values = True

class InvoiceItemResponse(NewInvoiceItem):
    invoice_id: UUID

    class Config:   
        from_attributes = True

class InvoiceDetailResponse(InvoiceResponse):
    items: List[InvoiceItemResponse]



