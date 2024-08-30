from datetime import datetime
import uuid
from sqlalchemy import UUID, Enum, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped

from .base import Base
from app.model.invoice import InvoiceModel, InvoiceStatus

class Invoice(Base):
    __tablename__ = 'invoice'

    id: Mapped[str] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[int] = Column(Integer)
    raise_date: Mapped[datetime] = Column(DateTime)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
    summary: Mapped[str] = Column(String)
    payment_method: Mapped[str] = Column(String)
    payment_info: Mapped[int] = Column(Integer, ForeignKey('payment_info.id'), nullable=True)
    client_email: Mapped[str] = Column(String)
    status: Mapped[InvoiceStatus] = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)

    def __init__(self, *, client_id, summary):
        self.client_id = client_id
        self.raise_date = datetime.now()
        self.summary = summary
        self.status = InvoiceStatus.PENDING

    def asDataClass(self) -> InvoiceModel:
        if self is None:
            return None
        return InvoiceModel(
            id=self.id,
            client_id=self.client_id,
            raise_date=self.raise_date,
            updated_at=self.updated_at,
            client_email=self.client_email,
            summary=self.summary,
            payment_method=self.payment_method,
            payment_info=self.payment_info,
            status=self.status
        )