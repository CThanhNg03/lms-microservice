import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from app.di.unit_of_work import AbstractUnitOfWork
from app.model.exception import InvoiceError
from app.model.invoice import INVOICE_TTL, CreateInvoiceModel, CreateOrderModel, GetInvoiceItemParamsModel, GetInvoiceParamsModel, InvoiceDetailModel, InvoiceItemModel, InvoiceModel, InvoiceStatus, TransactionModel
from app.model.pagination import PaginationParamsModel
from app.model.payment_info import CreatePaymentModel, GetPaymentParamsModel, PaymentInfoModel
from app.repositories.abstraction.payment import AbstractPaymentRepository
from app.setting.setting import logger

async def make_invoice(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], order: CreateOrderModel):
    async with async_unit_of_work as uow:
        cur_invoice: List[InvoiceModel] = await uow.repo.list_invoice(params=GetInvoiceParamsModel(status=InvoiceStatus.PENDING, client_id=order.client_id), pagin=None)
        if len(cur_invoice) > 0:
            for invoice in cur_invoice:
                await uow.repo.update_invoice_status(invoice.id, "CANCELED")
        if order.payment_method == "credit_card":
            payment = await uow.repo.get_payment_info(GetPaymentParamsModel(
                client_id=order.client_id,
                card_number=order.payment_info.card_number,
            ))
            if payment is None:
                payment = await uow.repo.create_payment_info(
                    client_id=order.client_id,
                    payment_info=CreatePaymentModel(**order.payment_info.__dict__)
                )
        else:
            payment = None
        order.payment_info = payment
        invoice = order.__dict__.copy()
        invoice.pop("items")
        invoice["payment_info"] = payment.id if payment else None
        invoice = CreateInvoiceModel(**invoice)
        newInvoice = await uow.repo.create_invoice(invoice)
        total = 0
        for item in order.items:
            await uow.repo.create_invoice_item(
                InvoiceItemModel(
                    invoice_id=newInvoice.id,
                    **item.__dict__
            ))
            total += item.amount
        return TransactionModel(
            invoice=newInvoice.id,
            payment_info=order.payment_info if order.payment_method == "credit_card" else None,
            payment_method=order.payment_method,
            amount=total,
            summary=newInvoice.summary
        )

async def pay_invoice(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], invoice_id):
    async with async_unit_of_work as uow:
        return (await uow.repo.update_invoice_status(invoice_id, "PAID")).updated_at

async def cancel_invoice(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], invoice_id):
    async with async_unit_of_work as uow:
        return (await uow.repo.update_invoice_status(invoice_id, "CANCELED")).updated_at
    
async def get_report(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], params: GetInvoiceItemParamsModel):
    async with async_unit_of_work as uow:
        params.start_date = datetime.strptime(params.start_date, "%Y-%m-%d")
        params.end_date = datetime.strptime(params.end_date, "%Y-%m-%d")+timedelta(days=1)
        params.status = InvoiceStatus.PAID
        return await uow.repo.list_invoice_item(params=params, pagin=None)
        
async def list_invoice(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], *, params: Optional[GetInvoiceParamsModel], pagin: Optional[PaginationParamsModel]):
    async with async_unit_of_work as uow:
        return await uow.repo.list_invoice(params, pagin)
    
async def get_invoice(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], invoice_id):
    async with async_unit_of_work as uow:
        invoice = await uow.repo.get_invoice(invoice_id)
        if invoice is None:
            raise InvoiceError("Invoice not found")
        params = GetInvoiceItemParamsModel(...)
        params.invoice_id = invoice_id
        items = await uow.repo.list_invoice_item(
            params=params, 
            pagin=None)
        items = [item.__dict__ for item in items]
        for item in items:
            item.pop('_sa_instance_state')
            item["invoice_id"] = str(item["invoice_id"])
        total = sum([item["amount"] for item in items])

        return InvoiceDetailModel(
            invoice_id=invoice.id,
            client_id=invoice.client_id,
            summary=invoice.summary,
            payment_method=invoice.payment_method,
            payment_info=invoice.payment_info,
            raise_date=invoice.raise_date,
            client_email=invoice.client_email,
            items=[InvoiceItemModel(**item) for item in items],
            total=total,
            updated_at=invoice.updated_at
        ), invoice.status
    
async def list_invoice_item(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], params: Optional[GetInvoiceItemParamsModel], pagin: Optional[PaginationParamsModel]):
    async with async_unit_of_work as uow:
        return await uow.repo.list_invoice_item(params, pagin)
    
async def cancel_outdated_invoice(async_unit_of_work: AbstractUnitOfWork[AbstractPaymentRepository], invoice_id):
    async with async_unit_of_work as uow:
        invoice = await uow.repo.get_invoice(invoice_id)
        if invoice is None:
            raise InvoiceError("Invoice not found")
        await asyncio.sleep(INVOICE_TTL * 60)
        if invoice.status == InvoiceStatus.PENDING:
            await uow.repo.update_invoice_status(invoice_id, "CANCELED")