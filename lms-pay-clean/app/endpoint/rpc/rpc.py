import asyncio
from app.common.utils.mail import send_invoice_mail
from app.common.utils.mapper import object_to_dict, pydantic_to_dataclass
from app.di.unit_of_work import AbstractUnitOfWork
from app.endpoint.mapper.invoice import InvoiceRequestMapper, InvoiceResponseMapper
from app.endpoint.rpc.rmq_service import RMQService

from app.repositories.paygateway import paymentGateway
from app.usecase import payment as payment_uc
from app.di.dependency_injection import payment_injector
from app.model.invoice import CreateOrderModel, GetInvoiceItemParamsModel, InvoiceDetailModel, InvoiceStatus
from ..schema.invoice import InvoiceItemReportResponse, NewOrder, ReportRequest
from app.setting.setting import logger

rabbit = RMQService()

@rabbit.rpc(queue_name="order")
async def order(body: NewOrder):
    async_uow = payment_injector.get(AbstractUnitOfWork)
    # order_data = CreateOrderModel(**body.model_dump())
    order_data = InvoiceRequestMapper.create_order(body)
    trans = await payment_uc.make_invoice(async_uow, order_data)
    asyncio.create_task(payment_uc.cancel_outdated_invoice(async_uow, trans.invoice))
    result = await paymentGateway.process_payment(transaction=object_to_dict(trans))
    if result.get("status"):
        update = await payment_uc.pay_invoice(async_uow, trans.invoice)
        invoice = InvoiceResponseMapper.to_invoice_detail(invoice=body, total=trans.amount, update=update, invoice_id=trans.invoice)
        asyncio.create_task(send_invoice_mail(invoice))
    return result

@rabbit.rpc(queue_name="report")
async def report(body: ReportRequest):
    async_uow = payment_injector.get(AbstractUnitOfWork)
    report_data = InvoiceRequestMapper.get_items_params(body)
    result = await payment_uc.get_report(async_uow, report_data)
    data = InvoiceResponseMapper.to_list_response(result, type=InvoiceItemReportResponse)
    return {
        "status": True,
        "message": "Success",
        "data": InvoiceResponseMapper.to_dict(data)
    }
