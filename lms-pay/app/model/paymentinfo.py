from sqlalchemy import Column, Integer, String

from app.model.base import Base

class PaymentInfo(Base):
    __tablename__ = 'payment_info'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    card_holder = Column(String)
    card_number = Column(String)
    cvv = Column(String)
    exp_date = Column(String)
    billing_address = Column(String)

    def __init__(self, *, client_id: int, card_holder: str, card_number: str, cvv: str, exp_date: str, billing_address: str):
        self.client_id = client_id
        self.card_holder = card_holder
        self.card_number = card_number
        self.cvv = cvv
        self.exp_date = exp_date
        self.billing_address = billing_address