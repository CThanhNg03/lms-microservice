import abc
from typing import List, Optional
from uuid import UUID

from app.model.invoice import GetInvoiceItemParamsModel, GetInvoiceParamsModel, InvoiceItemModel, InvoiceModel
from app.model.payment_info import GetPaymentParamsModel, PaymentInfoModel


class AbstractPaymentRepository(abc.ABC):
    session: any

    @abc.abstractmethod
    async def get_invoice(self, id: UUID) -> InvoiceModel | None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def list_invoice(self, params: Optional[GetInvoiceParamsModel]) -> List[InvoiceModel]:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def create_invoice(self, invoice: InvoiceModel) -> InvoiceModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def update_invoice(self, id: UUID, invoice: InvoiceModel) -> InvoiceModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def update_invoice_status(self, id: UUID, status: str) -> InvoiceModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def delete_invoice(self, id: UUID) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_invoice_item(self, id: UUID) -> InvoiceItemModel | None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def list_invoice_item(self, params: GetInvoiceItemParamsModel) -> List[InvoiceItemModel]:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def create_invoice_item(self, invoice_item: InvoiceItemModel) -> InvoiceItemModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def update_invoice_item(self, id: UUID, invoice_item: InvoiceItemModel) -> InvoiceItemModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def delete_invoice_item(self, id: UUID) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_payment_info(self, params: GetPaymentParamsModel) -> PaymentInfoModel | None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def create_payment_info(self, payment_info: PaymentInfoModel) -> PaymentInfoModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def update_payment_info(self, client_id, payment_info: PaymentInfoModel) -> PaymentInfoModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def delete_payment_info(self, client_id) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_item_total(self, invoice_id: UUID) -> int:
        raise NotImplementedError
    
    
    
    

