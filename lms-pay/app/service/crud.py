from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import TIMESTAMP, cast, func, select, insert, update

from app.core.db import get_db
from app.model import InvoiceItem, PaymentInfo, Invoice, InvoiceStatus
from app.schema import InvoiceUpdate, NewInvoice, NewInvoiceItem, NewPaymentInfo, ReportRequest


@asynccontextmanager
async def session():
    async for db in get_db():
        yield db

async def create_payment_info(*, payment_info: NewPaymentInfo):
    async with session() as db:
        stmt = insert(PaymentInfo).values(**payment_info.model_dump()).returning(PaymentInfo.id)
        result = await db.execute(stmt)
        await db.commit()
        return {"payment_id": result.scalar()}

async def get_payment_info(*, client_id, card_number = None):
    async with session() as db:
        stmt = select(PaymentInfo).where(PaymentInfo.client_id == client_id)
        if card_number:
            stmt = stmt.where(PaymentInfo.card_number == card_number)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().all()
    
async def update_payment_info(*,info_id, client_id, payment_method, detail):
    async with session() as db:
        stmt = update(PaymentInfo).where(PaymentInfo.id == info_id).values(client_id=client_id, payment_method=payment_method, detail=detail).returning(PaymentInfo.id)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().first()
    
async def delete_payment_info(*, client_id, payment_method):
    async with session() as db:
        stmt = insert(PaymentInfo).where(PaymentInfo.client_id == client_id, PaymentInfo.payment_method == payment_method)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().first()

async def create_invoice(*, invoice: NewInvoice, items: List[NewInvoiceItem]):
    async with session() as db:
        if invoice.payment_method == "credit_card":
            findPayment = select(PaymentInfo.id).where(PaymentInfo.client_id == invoice.client_id, PaymentInfo.card_number == invoice.payment_info.card_number)
            payment = await db.execute(findPayment)
            payment_id = payment.scalar()
            if payment_id is None:
                newPayment = insert(PaymentInfo).values(client_id=invoice.client_id, **invoice.payment_info.model_dump()).returning(PaymentInfo.id)
                payment = await db.execute(newPayment)
                payment_id = payment.scalar()
        else:
            payment_id = None
        newInvoice = insert(Invoice).values(
            client_id=invoice.client_id, 
            summary=invoice.summary, 
            payment_method=invoice.payment_method,
            payment_info=payment_id,
            raise_date=invoice.raise_date
        ).returning(Invoice.id)
        result = await db.execute(newInvoice)
        invoice_id = result.scalar()
        for item in items:
            newInvoiceItem = insert(InvoiceItem).values(
                invoice_id=invoice_id, 
                course_id=item.course_id, 
                amount=item.amount,
                author_id=item.author_id
            )
            await db.execute(newInvoiceItem)
        await db.commit()
        return invoice_id
    
async def get_invoice(*, invoice_id):
    async with session() as db:
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().first()
    
async def get_transaction(*, invoice_id):
    async with session() as db:
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        result = await db.execute(stmt)
        invoice = result.scalar()
        if invoice is None:
            return None
        if invoice.payment_info:
            stmt = select(PaymentInfo).where(PaymentInfo.id == invoice.payment_info)
            payment = await db.execute(stmt)
            payment_info = payment.scalar().__dict__
        else:
            payment_info = None
        stmt = select(func.sum(InvoiceItem.amount).label('total')).where(InvoiceItem.invoice_id == invoice_id).group_by(InvoiceItem.invoice_id)
        total = await db.execute(stmt)
        amount = total.scalar()
        await db.commit()
        return {"payment_method": invoice.payment_method,
                "payment_info": payment_info, 
                "amount": amount, 
                "summary": invoice.summary, 
                "invoice_id": invoice_id}

        
async def get_invoices(*, client_id):
    async with session() as db:
        stmt = select(Invoice).where(Invoice.client_id == client_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().all()

async def update_invoice_status(*, invoice_id, status):
    async with session() as db:
        stmt = update(Invoice).where(Invoice.id == invoice_id).values(status=status, updated_at=datetime.now()).returning(Invoice.id)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar()
    
async def get_report(*, request: ReportRequest):
    async with session() as db:
        request.start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        request.end_date = datetime.strptime(request.end_date, "%Y-%m-%d")+timedelta(days=1)
        stmt = select(InvoiceItem, Invoice.updated_at).join(Invoice).where(
            Invoice.raise_date.between(
                request.start_date, 
                request.end_date),
            Invoice.status == InvoiceStatus.PAID
        )
        if request.author_id: 
            stmt = stmt.where(InvoiceItem.author_id == request.author_id)
        if len(request.course_id) > 0:
            stmt = stmt.where(InvoiceItem.course_id.in_(request.course_id))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalars().all()