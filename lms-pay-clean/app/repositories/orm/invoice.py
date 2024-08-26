from datetime import datetime
import uuid
from sqlalchemy import UUID, Enum, Column, ForeignKey, Integer, String, DateTime
import enum

from .base import Base

class InvoiceStatus(enum.Enum):
    PENDING = 1
    PAID = 2
    CANCELED = 3

class Invoice(Base):
    __tablename__ = 'invoice'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(Integer)
    raise_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.now)
    summary = Column(String)
    payment_method = Column(String)
    payment_info = Column(Integer, ForeignKey('payment_info.id'), nullable=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)

    def __init__(self, *, client_id, summary):
        self.client_id = client_id
        self.raise_date = datetime.now()
        self.summary = summary
        self.status = InvoiceStatus.PENDING
