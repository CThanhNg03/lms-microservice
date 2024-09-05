from typing import List, Type, Union

from pydantic import BaseModel
from app.endpoint.schema.invoice import InvoiceDetailResponse, InvoiceItemReportResponse, InvoiceItemResponse, InvoiceResponse, NewInvoice, NewInvoiceItem, NewOrder, NewPaymentInfo, PaginationResponse, ReportRequest
from app.model.invoice import CreateInvoiceItemModel, CreateOrderModel, GetInvoiceItemParamsModel, GetInvoiceParamsModel, InvoiceDetailModel, InvoiceItemModel, InvoiceModel, InvoiceReportModel, InvoiceStatus
from app.model.pagination import PaginationModel, PaginationParamsModel
from app.model.payment_info import CreatePaymentModel


class InvoiceRequestMapper:
    """
    This class is responsible for mapping the request data to the model data.
    """
    @classmethod
    def create_payment(cls, payment_info: NewPaymentInfo) -> CreatePaymentModel:
        return CreatePaymentModel(
            card_holder=payment_info.card_holder,
            card_number=payment_info.card_number,
            cvv=payment_info.cvv,
            exp_date=payment_info.exp_date,
            billing_address=payment_info.billing_address
        )
    
    @classmethod
    def create_item(cls, item_data: NewInvoiceItem) -> CreateInvoiceItemModel:
        return CreateInvoiceItemModel(
            course_id=item_data.course_id,
            author_id=item_data.author_id,
            amount=item_data.amount,
            course_name=item_data.course_name
        ) 
    
    @classmethod
    def create_order(cls, order_request: NewOrder) -> CreateOrderModel:
        return CreateOrderModel(
            client_id=order_request.client_id,
            raise_date=order_request.raise_date,
            summary=order_request.summary,
            payment_method=order_request.payment_method,
            payment_info=cls.create_payment(order_request.payment_info),
            client_email=order_request.client_email,
            items=[cls.create_item(item) for item in order_request.items]
        )
    
    @classmethod
    def get_items_params(cls, params: ReportRequest) -> GetInvoiceItemParamsModel:
        return GetInvoiceItemParamsModel(
            start_date=params.start_date,
            end_date=params.end_date,
            author_id=params.author_id,
            course_id=params.course_id,
            status=params.status
        )

    @classmethod
    def get_invoice_params(cls, client_id: int | None) -> GetInvoiceParamsModel:
        return GetInvoiceParamsModel(client_id=client_id)

    @classmethod
    def to_pagin_params(cls, pagin: dict) -> PaginationParamsModel:
        return PaginationParamsModel(**pagin)
    
class InvoiceResponseMapper:
    """
    This class is responsible for mapping the model data to the response data.
    """
    @classmethod
    def to_item_response(cls, item: InvoiceItemModel, invoice=None) -> InvoiceItemResponse:
        return InvoiceItemResponse(
            invoice_id=invoice if invoice else item.invoice_id,
            course_id=item.course_id,
            author_id=item.author_id,
            amount=item.amount,
            course_name=item.course_name
        )
    
    @classmethod
    def to_item_report(cls, item: InvoiceReportModel) -> InvoiceItemReportResponse:
        return InvoiceItemReportResponse(
            invoice_id=item.invoice_id,
            course_id=item.course_id,
            author_id=item.author_id,
            amount=item.amount,
            course_name=item.course_name,
            updated_at=item.updated_at
        )
    
    @classmethod 
    def to_invoice_response(cls, invoice: InvoiceModel) -> InvoiceResponse:
        return InvoiceResponse(
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
    
    @classmethod
    def to_invoice_detail(cls, *, invoice: NewOrder, total, update, invoice_id) -> InvoiceDetailModel:
        return InvoiceDetailModel(
            invoice_id=invoice_id,
            client_id=invoice.client_id,
            raise_date=invoice.raise_date,
            updated_at=update,
            client_email=invoice.client_email,
            summary=invoice.summary,
            payment_method=invoice.payment_method,
            payment_info=invoice.payment_info,
            items=[cls.to_item_response(item, invoice=invoice_id) for item in invoice.items],
            total=total
        )
    
    @classmethod
    def to_list_response(cls, data: list, type: Type) -> list:
        if type == InvoiceItemResponse:
            return [cls.to_item_response(item) for item in data]
        if type == InvoiceResponse:
            return [cls.to_invoice_response(item) for item in data]
        if type == InvoiceItemReportResponse:
            return [cls.to_item_report(item) for item in data]

    @classmethod
    def to_paginated_response(cls, data: PaginationModel, type: Type) -> PaginationResponse:
        return PaginationResponse(
            page=data.page,
            limit=data.limit,
            skip=data.skip,
            total=data.total,
            items = cls.to_list_response(data.items, type)
        )
    
    @classmethod
    def to_detail_response(cls, data: InvoiceDetailModel, status: InvoiceStatus) -> InvoiceDetailResponse:
        return InvoiceDetailResponse(
            **cls.to_invoice_response(data).model_dump(),
            items=[cls.to_item_response(item) for item in data.items],
            status=status
        )
    
    @classmethod
    def to_dict(cls, data: Union[BaseModel, List[BaseModel]]):
        if isinstance(data, list):
            return [item.model_dump(mode='json') for item in data]
        return data.model_dump(mode='json')

    