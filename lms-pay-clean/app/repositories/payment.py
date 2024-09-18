from turtle import up
from typing import List, Optional
from uuid import UUID
from sqlalchemy import delete, func, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils.pagination import paginate
from app.model.invoice import GetInvoiceItemParamsModel, GetInvoiceParamsModel, InvoiceItemModel, InvoiceModel, InvoiceReportModel
from app.model.pagination import PaginationModel, PaginationParamsModel
from app.model.payment_info import CreatePaymentModel, GetPaymentParamsModel, PaymentInfoModel
from app.repositories.abstraction.payment import AbstractPaymentRepository
from app.repositories.mapper.invoice import InvoiceOrmMapper
from app.repositories.mapper.invoice_item import InvoiceItemOrmMapper
from app.repositories.mapper.paymentinfo import PaymentInfoOrmMapper
from app.repositories.orm.invoice import Invoice, InvoiceStatus
from app.repositories.orm.invoiceitem import InvoiceItem
from app.repositories.orm.payment_info import PaymentInfo
from app.setting.setting import logger


class PaymentRepository(AbstractPaymentRepository):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
    
    async def get_invoice(self, id: UUID) -> InvoiceModel | None:
        stmt = select(Invoice).where(Invoice.id == id)
        result = await self.session.execute(stmt)
        return result.scalar().asDataClass()

    async def list_invoice(self, params: Optional[GetInvoiceParamsModel], pagin: Optional[PaginationParamsModel]) -> List[InvoiceModel] | PaginationModel[InvoiceItem]:
        stmt = select(Invoice)
        if params.client_id:
            stmt = stmt.where(Invoice.client_id == params.client_id)
        if params.status:
            stmt = stmt.where(Invoice.status == params.status)
        if pagin:
            stmt = paginate(stmt, pagin)
            result = await self.session.execute(stmt)
            count_stmt = select(func.count(Invoice.id)).select_from(stmt)
            count = await self.session.execute(count_stmt)
            return PaginationModel[InvoiceItem](
                items=[InvoiceOrmMapper.to_domain(item) for item in result.scalars().all()], 
                total=count.scalar(), 
                **pagin.__dict__)    
        result = await self.session.execute(stmt)
        return [InvoiceOrmMapper.to_domain(item) for item in result.scalars().all()]
    
    async def create_invoice(self, invoice: InvoiceModel) -> InvoiceModel:
        stmt = insert(Invoice).values(**invoice.__dict__).returning(Invoice)
        result = await self.session.execute(stmt)
        return InvoiceOrmMapper.to_domain(result.scalar())
    
    async def update_invoice(self, id: UUID, invoice: InvoiceModel) -> InvoiceModel:
        stmt = update(Invoice).where(Invoice.id == id).values(**invoice.__dict__).returning(Invoice)
        result = await self.session.execute(stmt)
        return InvoiceOrmMapper.to_domain(result.scalar())
    
    async def delete_invoice(self, id: UUID) -> None:
        stmt = delete(Invoice).where(Invoice.id == id)
        await self.session.execute(stmt)

    async def get_invoice_item(self, id: UUID) -> InvoiceModel | None:
        stmt = select(Invoice).where(Invoice.id == id)
        result = await self.session.execute(stmt)
        return InvoiceItemOrmMapper.to_domain(result.scalar())
    
    async def list_invoice_item(self, params: GetInvoiceItemParamsModel, pagin: Optional[PaginationParamsModel]) -> List[InvoiceReportModel] | PaginationModel[InvoiceItemModel]:
        stmt = select(InvoiceItem, Invoice.updated_at).join(Invoice)
        if params.start_date and params.end_date:
            stmt = stmt.where(Invoice.updated_at.between(params.start_date, params.end_date))
        if params.status:
            stmt = stmt.where(Invoice.status == params.status)
        if params.author_id:
            stmt = stmt.where(InvoiceItem.author_id == params.author_id)
        if params.course_id:
            stmt = stmt.where(InvoiceItem.course_id.in_(params.course_id))
        if params.invoice_id:
            stmt = stmt.where(InvoiceItem.invoice_id == params.invoice_id)
        if pagin:
            pagination = paginate(stmt, pagin)
            result = await self.session.execute(pagination)
            items = [InvoiceItemOrmMapper.to_domain(item) for item in result.scalars().all()]
            count_stmt = select(func.count('*')).select_from(stmt)
            count = await self.session.execute(count_stmt)
            return PaginationModel[InvoiceItemModel](items=items, total=count.scalar(), **pagin.__dict__)
        result = await self.session.execute(stmt)
        res = result.all()
        return [InvoiceItemOrmMapper.to_report_domain(item) for item in res]
    
    async def update_invoice_status(self, id: UUID, status: str) -> InvoiceModel:
        update_status = InvoiceStatus[status]
        stmt = update(Invoice).where(Invoice.id == id).values(status=update_status).returning(Invoice)
        result = await self.session.execute(stmt)
        return InvoiceOrmMapper.to_domain(result.scalar())
    
    async def create_invoice_item(self, invoice_item: InvoiceItemModel) -> InvoiceItemModel:
        stmt = insert(InvoiceItem).values(**invoice_item.__dict__).returning(InvoiceItem)
        result = await self.session.execute(stmt)
        return result.scalar().asDataClass()
    
    async def update_invoice_item(self, id: UUID, invoice_item: InvoiceItemModel) -> InvoiceItemModel:
        stmt = update(InvoiceItem).where(InvoiceItem.id == id).values(**invoice_item.__dict__).returning(InvoiceItem)
        result = await self.session.execute(stmt)
        return InvoiceItemOrmMapper.to_domain(result.scalar())
    
    async def delete_invoice_item(self, id: UUID) -> None:
        stmt = delete(InvoiceItem).where(InvoiceItem.id == id)
        await self.session.execute(stmt)

    async def get_payment_info(self, params: GetPaymentParamsModel) -> PaymentInfoModel | None:
        stmt = select(PaymentInfo).where(PaymentInfo.client_id == params.client_id)
        if params.card_number:
            stmt = stmt.where(PaymentInfo.card_number == params.card_number)
        result = await self.session.execute(stmt)
        return PaymentInfoOrmMapper.to_domain(result.scalar())
    
    async def create_payment_info(self, payment_info: CreatePaymentModel, client_id: int) -> PaymentInfoModel:
        stmt = insert(PaymentInfo).values(client_id = client_id ,**payment_info.__dict__).returning(PaymentInfo)
        result = await self.session.execute(stmt)
        return PaymentInfoOrmMapper.to_domain(result.scalar())
    
    async def update_payment_info(self, client_id, payment_info: PaymentInfoModel) -> PaymentInfoModel:
        stmt = update(PaymentInfo).where(PaymentInfo.client_id == client_id).values(**payment_info.__dict__).returning(PaymentInfo)
        result = await self.session.execute(stmt)
        return PaymentInfoOrmMapper.to_domain(result.scalar())
    
    async def delete_payment_info(self, client_id) -> None:
        stmt = delete(PaymentInfo).where(PaymentInfo.client_id == client_id)
        await self.session.execute(stmt)

    async def get_item_total(self, invoice_id: UUID) -> int:
        stmt = select(func.sum(InvoiceItem.amount)).where(InvoiceItem.invoice_id == invoice_id)
        result = await self.session.execute(stmt)
        return result.scalar()
