from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PaymentInfoModel:
    id: int
    client_id: int
    card_holder: str 
    card_number: str 
    cvv: str 
    exp_date: datetime 
    billing_address: str 

@dataclass
class GetPaymentParamsModel:
    client_id: int
    card_number: Optional[str] = None

@dataclass
class CreatePaymentModel:
    card_holder: str 
    card_number: str 
    cvv: str 
    exp_date: datetime 
    billing_address: str
