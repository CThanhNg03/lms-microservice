from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.model.payment_info import PaymentInfoModel

from .base import Base

class PaymentInfo(Base):
    __tablename__ = 'payment_info'

    id: Mapped[int] = Column(Integer, primary_key=True)
    client_id: Mapped[int] = Column(Integer)
    card_holder: Mapped[str] = Column(String)
    card_number: Mapped[str] = Column(String)
    cvv: Mapped[str] = Column(String)
    exp_date: Mapped[str] = Column(String)
    billing_address: Mapped[str] = Column(String)

    def __init__(self, *, client_id: int, card_holder: str, card_number: str, cvv: str, exp_date: str, billing_address: str):
        self.client_id = client_id
        self.card_holder = card_holder
        self.card_number = card_number
        self.cvv = cvv
        self.exp_date = exp_date
        self.billing_address = billing_address
    
    def asDataClass(self) -> PaymentInfoModel:
        if self is None:
            return None
        
        return PaymentInfoModel(
            id=self.id,
            client_id=self.client_id,
            card_holder=self.card_holder,
            card_number=self.card_number,
            cvv=self.cvv,
            exp_date=self.exp_date,
            billing_address=self.billing_address
        )