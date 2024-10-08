from app.model.invoice import InvoiceModel
from app.repositories.mapper.base import BaseOrmMapper
from app.repositories.orm.invoice import Invoice


class InvoiceOrmMapper(BaseOrmMapper):
    """
    This class is responsible for mapping the ORM data to the model data and vice versa of table *invoice*.
    """
    @staticmethod
    def to_domain(invoice: Invoice) -> InvoiceModel:
        return InvoiceModel(
            id=invoice.id,
            client_id=invoice.client_id,
            raise_date=invoice.raise_date,
            updated_at=invoice.updated_at,
            client_email=invoice.client_email,
            summary=invoice.summary,
            payment_method=invoice.payment_method,
            payment_info=invoice.payment_info,
            status=invoice.status
        )

    @staticmethod
    def to_orm(invoice: InvoiceModel) -> Invoice:
        return Invoice(
            id=invoice.id,
            client_id=invoice.client_id,
            raise_date=invoice.raise_date,
            updated_at=invoice.updated_at,
            client_email=invoice.client_email,
            summary=invoice.summary,
            payment_method=invoice.payment_method,
            payment_info=invoice.payment_info,
            status=invoice.status
        )