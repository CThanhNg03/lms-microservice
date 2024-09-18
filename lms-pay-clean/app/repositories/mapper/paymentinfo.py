from app.model.payment_info import PaymentInfoModel
from app.repositories.mapper.base import BaseOrmMapper
from app.repositories.orm.payment_info import PaymentInfo


class PaymentInfoOrmMapper(BaseOrmMapper):
    """
    This class is responsible for mapping the ORM data to the model data and vice versa of table *payment_info*.
    """
    @staticmethod
    def to_domain(data: PaymentInfo) -> PaymentInfoModel:
        if not data:
            return None
        return PaymentInfoModel(
            id=data.id,
            client_id=data.client_id,
            card_number=data.card_number,
            card_holder=data.card_holder,
            exp_date=data.exp_date,
            billing_address=data.billing_address,
            cvv=data.cvv
        )
    
    @staticmethod
    def to_orm(data: PaymentInfoModel) -> PaymentInfo:
        if not data:
            return None
        return PaymentInfo(
            id=data.id,
            client_id=data.client_id,
            card_number=data.card_number,
            card_holder=data.card_holder,
            exp_date=data.exp_date,
            billing_address=data.billing_address,
            cvv=data.cvv
        )
