from typing import List
from fastapi import FastAPI, HTTPException

from app.core.db import engine
from app.service import crud
from app.model.base import Base
from app.model.invoice import InvoiceStatus
from app.service.pay_gateway import paymentGateway
from app.schema import InvoiceUpdate, NewInvoice, NewInvoiceItem, NewOrder, NewPaymentInfo, PaymentResult, ReportRequest
from app.service.rmq_server import RMQServer

class PayApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rmqService = [RMQServer(queue="order"), RMQServer(queue="report")]

app = PayApp()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    for service in app.rmqService:
        await service.run()

@app.on_event("shutdown")
async def shutdown():
    for service in app.rmqService:
        await service.close()

@app.get("/payment_info")
async def get_payment_info(client_id: int, payment_method: str = None):
    result = await crud.get_payment_info(client_id=client_id, payment_method=payment_method)
    return result

@app.post("/payment_info", status_code=201)
async def create_payment_info(payment_info: NewPaymentInfo):
    result = await crud.create_payment_info(client_id=payment_info.client_id, payment_method=payment_info.payment_method, detail=payment_info.detail)
    return result

@app.put("/payment_info/{info_id}")
async def update_payment_info(info_id: int, payment_info: NewPaymentInfo):
    result = await crud.update_payment_info(info_id=info_id, client_id=payment_info.client_id, payment_method=payment_info.payment_method, detail=payment_info.detail)
    return result

@app.delete("/payment_info/{info_id}")
async def delete_payment_info(info_id: int):
    result = await crud.delete_payment_info(info_id=info_id)
    return result

@app.post("/invoice", status_code=201)
async def create_invoice(invoice: NewInvoice, items: List[NewInvoiceItem]):
    result = await crud.create_invoice(invoice=invoice, items=items)
    return result

@app.get("/cancel_invoice/{invoice_id}")
async def cancel_invoice(invoice_id: int):
    invoice = await crud.get_transaction(invoice_id=invoice_id)
    if invoice is None:
        return HTTPException(status_code=404, detail="Invoice not found")
    if invoice['status'] != InvoiceStatus.PENDING:
        return HTTPException(status_code=400, detail="Invoice is not pending")
    result = await crud.update_invoice_status(invoice=InvoiceUpdate(invoice_id=invoice_id, status=InvoiceStatus.CANCELED))
    return result

@app.post("/checkout/{invoice_id}")
async def checkout(invoice_id: int, payment_info: NewPaymentInfo):
    payment = await crud.find_payment_info(client_id=payment_info.client_id, payment_method=payment_info.payment_method)
    invoice = await crud.get_transaction(invoice_id=invoice_id)
    if invoice is None:
        return HTTPException(status_code=404, detail="Invoice not found")
    if invoice['status'] != InvoiceStatus.PENDING:
        return HTTPException(status_code=400, detail="Invoice is not pending")
    transaction = await paymentGateway.process_payment(payment_info=invoice["payment_info"], amount=invoice["amount"])
    if not transaction["succeded"]:
        return HTTPException(status_code=400, detail=f"Payment failed: {transaction['message']}")
    result = await crud.update_invoice_status(invoice=InvoiceUpdate(invoice_id=invoice_id, status=InvoiceStatus.PAID))
    return {"message": f"Payment {result} processed successfully"}

@app.webhooks.post("/invoice/{invoice_id}")
async def invoice_webhook(invoice_id: int, data: PaymentResult):
    invoice = await crud.get_transaction(invoice_id=invoice_id)
    if invoice is None:
        return HTTPException(status_code=404, detail="Invoice not found")
    if invoice['status'] != InvoiceStatus.PENDING:
        return HTTPException(status_code=400, detail="Invoice is not pending")
    if data.status != "success":
        return HTTPException(status_code=400, detail=f"Payment failed: {data.message}")
    result = await crud.update_invoice_status(invoice=InvoiceUpdate(invoice_id=invoice_id, status=InvoiceStatus.PAID))
    return {"message": f"Payment {result} processed successfully"}

@app.post("/order")
async def new_order(body: NewOrder):
    return {"message": "Order received"}

@app.post("/report")
async def new_report(body: ReportRequest):
    return {"message": "Report received"}