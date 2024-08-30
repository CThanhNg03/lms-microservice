from sqlalchemy import UUID, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped

from app.model.invoice import InvoiceItemModel
from .base import Base


class InvoiceItem(Base):
    __tablename__ = 'invoice_item'

    invoice_id: Mapped[str] = Column(UUID(as_uuid=True), ForeignKey('invoice.id'), primary_key=True)
    course_id: Mapped[int] = Column(Integer, primary_key=True)
    author_id: Mapped[int] = Column(Integer)
    amount: Mapped[float] = Column(Float)
    course_name: Mapped[str] = Column(String)

    def __init__(self, *, invoice_id, course_id, amount):
        self.invoice_id = invoice_id
        self.course_id = course_id
        self.amount = amount
    
    def asDataClass(self) -> InvoiceItemModel:
        if self is None:
            return None
        return InvoiceItemModel(
            invoice_id=self.invoice_id,
            course_id=self.course_id,
            author_id=self.author_id,
            amount=self.amount,
            course_name=self.course_name
        )