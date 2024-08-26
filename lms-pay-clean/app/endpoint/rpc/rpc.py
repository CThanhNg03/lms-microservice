from app.di.unit_of_work import AbstractUnitOfWork
from app.endpoint.rpc.rmq_service import RMQService

from app.repositories.paygateway import PaymentGateway
from app.usecase import payment as payment_uc
from app.di.dependency_injection import injector
from app.model.invoice import CreateOrderModel, GetInvoiceItemParamsModel
from .schema import NewOrder, PaymentResponse, ReportRequest

rabbit = RMQService()

@rabbit.rpc(queue_name="order")
async def order(body: NewOrder):
    async_uow = injector.get(AbstractUnitOfWork)
    order_data = CreateOrderModel(body.model_dump())
    trans = await payment_uc.make_invoice(async_uow, order_data)
    result = await PaymentGateway.process_payment(transaction=trans)
    if result.get("status"):
        await payment_uc.pay_invoice(async_uow, trans.invoice)
    return result

@rabbit.rpc(queue_name="report")
async def report(body: ReportRequest):
    async_uow = injector.get(AbstractUnitOfWork)
    report_data = GetInvoiceItemParamsModel(body.model_dump())
    result = await payment_uc.get_report(async_uow, report_data)
    return {
        "status": True,
        "message": "Success",
        "data": result
    }
