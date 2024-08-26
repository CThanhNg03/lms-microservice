from sqlalchemy import UUID, Column, ForeignKey, Integer
from .base import Base


class InvoiceItem(Base):
    __tablename__ = 'invoice_item'

    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoice.id'), primary_key=True)
    course_id = Column(Integer, primary_key=True)
    author_id = Column(Integer)
    amount = Column(Integer)

    def __init__(self, *, invoice_id, course_id, amount):
        self.invoice_id = invoice_id
        self.course_id = course_id
        self.amount = amount