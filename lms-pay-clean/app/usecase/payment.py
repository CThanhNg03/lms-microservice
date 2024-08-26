from datetime import datetime, timedelta
from typing import List

from app.di.unit_of_work import AbstractUnitOfWork
from app.model.invoice import CreateOrderModel, GetInvoiceItemParamsModel, InvoiceItemModel, TransactionModel
from app.model.payment_info import GetPaymentParamsModel, PaymentInfoModel

async def make_invoice(async_unit_of_work: AbstractUnitOfWork, order: CreateOrderModel):
    async with async_unit_of_work as uow:
        if order.payment_method == "credit_card":
            payment = await uow.repo.get_payment_info(GetPaymentParamsModel(
                client_id=order.client_id,
                payment_method=order.payment_method
            ))
            if payment is None:
                payment = await uow.repo.create_payment_info(PaymentInfoModel(
                    client_id=order.client_id,
                    **order.payment_info.__dict__
                ))
            payment_id = payment.id
        else:
            payment_id = None
        order.payment_info = payment_id
        newInvoice = await uow.repo.create_invoice(order)
        total = 0
        for item in order.items:
            await uow.repo.create_invoice_item(
                InvoiceItemModel(
                    invoice_id=newInvoice.id,
                    **item.__dict__
            ))
            total += item.amount
        return TransactionModel(
            invoice_id=newInvoice.id,
            payment_info=order.payment_info if order.payment_method == "credit_card" else None,
            payment_method=order.payment_method,
            amount=total,
            summary=newInvoice.summary
        )
    
async def make_transaction(async_unit_of_work: AbstractUnitOfWork, invoice_id):
    async with async_unit_of_work as uow:
        invoice = await uow.repo.get_invoice(invoice_id)
        if invoice is None:
            raise Exception("Invoice not found")
        if invoice.payment_info:
            payment = await uow.repo.get_payment_info(GetPaymentParamsModel(
                client_id=invoice.client_id,
                payment_method=invoice.payment_method
            ))
        else:
            payment = None
        total = await uow.repo.get_item_total(invoice_id)
        return TransactionModel(
            invoice_id=invoice_id,
            payment_info=payment,
            payment_method=invoice.payment_method,
            amount=total,
            summary=invoice.summary
        )

async def pay_invoice(async_unit_of_work: AbstractUnitOfWork, invoice_id):
    async with async_unit_of_work as uow:
        await uow.repo.update_invoice_status(invoice_id, "PAID")

async def cancel_invoice(async_unit_of_work: AbstractUnitOfWork, invoice_id):
    async with async_unit_of_work as uow:
        await uow.repo.update_invoice_status(invoice_id, "CANCELLED")

async def get_report(async_unit_of_work: AbstractUnitOfWork, params: GetInvoiceItemParamsModel):
    async with async_unit_of_work as uow:
        params.start_date = datetime.strptime(params.start_date, "%Y-%m-%d")
        params.end_date = datetime.strptime(params.end_date, "%Y-%m-%d")+timedelta(days=1)
        return await uow.repo.list_invoice_item(params)