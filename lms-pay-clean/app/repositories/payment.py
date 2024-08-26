from turtle import up
from typing import List, Optional
from uuid import UUID
from sqlalchemy import delete, func, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.invoice import GetInvoiceItemParamsModel, GetInvoiceParamsModel, InvoiceItemModel, InvoiceModel
from app.model.payment_info import GetPaymentParamsModel, PaymentInfoModel
from app.repositories.abstraction.payment import AbstractPaymentRepository
from app.repositories.orm.invoice import Invoice, InvoiceStatus
from app.repositories.orm.invoiceitem import InvoiceItem


class PaymentRepository(AbstractPaymentRepository):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
    
    async def get_invoice(self, id: UUID) -> InvoiceModel | None:
        stmt = select(Invoice).where(Invoice.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().first()

    async def list_invoice(self, params: Optional[GetInvoiceParamsModel]) -> List[InvoiceModel]:
        stmt = select(Invoice)
        if params:
            stmt = stmt.where(Invoice.client_id == params.client_id)
            stmt = stmt.offset(params.page*params.size).limit(params.size)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().all()
    
    async def create_invoice(self, invoice: InvoiceModel) -> InvoiceModel:
        stmt = insert(Invoice).values(**invoice.dict()).returning(Invoice)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return invoice
    
    async def update_invoice(self, id: UUID, invoice: InvoiceModel) -> InvoiceModel:
        stmt = update(Invoice).where(Invoice.id == id).values(**invoice.dict()).returning(Invoice)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
    
    async def delete_invoice(self, id: UUID) -> None:
        stmt = delete(Invoice).where(Invoice.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_invoice_item(self, id: UUID) -> InvoiceModel | None:
        stmt = select(Invoice).where(Invoice.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().first()
    
    async def list_invoice_item(self, params: GetInvoiceItemParamsModel) -> List[InvoiceItemModel]:
        stmt = select(InvoiceItem, Invoice.updated_at).join(Invoice).where(
            Invoice.raise_date.between(params.start_date, 
            params.end_date),
            Invoice.status == InvoiceStatus.PAID
        )
        if params.author_id:
            stmt = stmt.where(InvoiceItem.author_id.in_(params.author_id))
        if params.course_id:
            stmt = stmt.where(InvoiceItem.course_id.in_(params.course_id))
        if params.page:
            stmt = stmt.offset(params.page*params.size).limit(params.size)
           
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().all()
    
    async def update_invoice_status(self, id: UUID, status: str) -> InvoiceModel:
        status = InvoiceStatus.PAID if status == 'PAID' else InvoiceStatus.CANCELED
        stmt = update(Invoice).where(Invoice.id == id).values(status=status).returning(Invoice)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
    
    async def create_invoice_item(self, invoice_item: InvoiceItemModel) -> InvoiceItemModel:
        stmt = insert(InvoiceItem).values(**invoice_item.dict()).returning(InvoiceItem)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return invoice_item
    
    async def update_invoice_item(self, id: UUID, invoice_item: InvoiceItemModel) -> InvoiceItemModel:
        stmt = update(InvoiceItem).where(InvoiceItem.id == id).values(**invoice_item.dict()).returning(InvoiceItem)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
    
    async def delete_invoice_item(self, id: UUID) -> None:
        stmt = delete(InvoiceItem).where(InvoiceItem.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_payment_info(self, params: GetPaymentParamsModel) -> PaymentInfoModel | None:
        stmt = select(PaymentInfoModel).where(PaymentInfoModel.client_id == params.client_id)
        if params.card_number:
            stmt = stmt.where(PaymentInfoModel.card_number == params.card_number)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
    
    async def create_payment_info(self, payment_info: PaymentInfoModel) -> PaymentInfoModel:
        stmt = insert(PaymentInfoModel).values(**payment_info.dict()).returning(PaymentInfoModel)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return payment_info
    
    async def update_payment_info(self, client_id, payment_info: PaymentInfoModel) -> PaymentInfoModel:
        stmt = update(PaymentInfoModel).where(PaymentInfoModel.client_id == client_id).values(**payment_info.dict()).returning(PaymentInfoModel)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
    
    async def delete_payment_info(self, client_id) -> None:
        stmt = delete(PaymentInfoModel).where(PaymentInfoModel.client_id == client_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_item_total(self, invoice_id: UUID) -> int:
        stmt = select(func.sum(InvoiceItem.amount)).where(InvoiceItem.invoice_id == invoice_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
    
    
