from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse

from app.common.dependencies.auth import GetActiveUserDep
from app.common.dependencies.pagination import PaginDep
from app.common.utils.export import export_to_file
from app.endpoint.mapper.invoice import InvoiceRequestMapper, InvoiceResponseMapper
from app.endpoint.schema.invoice import InvoiceDetailResponse, InvoiceItemReportResponse, InvoiceItemResponse, InvoiceResponse, PaginationResponse, ReportRequest
from app.di.unit_of_work import AbstractUnitOfWork
from app.di.dependency_injection import payment_injector
from app.model.invoice import GetInvoiceItemParamsModel, GetInvoiceParamsModel
from app.model.pagination import PaginationParamsModel
from app.usecase import payment as payment_uc
from app.setting.setting import logger


invoice = APIRouter(tags=["invoice"])

@invoice.get("/", response_model=PaginationResponse[InvoiceResponse])
async def list_invoice(user: GetActiveUserDep, pagin: PaginDep, client_id: Optional[int] = None ):
    auow = payment_injector.get(AbstractUnitOfWork)
    pagin = InvoiceRequestMapper.to_pagin_params(pagin)
    params = InvoiceRequestMapper.get_invoice_params(client_id)
    result = await payment_uc.list_invoice(auow, params=params, pagin=pagin)
    return InvoiceResponseMapper.to_paginated_response(result, InvoiceResponse)

@invoice.get("/file/{type_file}")
async def get_invoice_file(type_file: str, user: GetActiveUserDep, client_id: Optional[int] = None):
    auow = payment_injector.get(AbstractUnitOfWork)
    params = InvoiceRequestMapper.get_invoice_params(client_id)
    result = await payment_uc.list_invoice(auow, params=params, pagin=None)
    result = [InvoiceResponseMapper.to_invoice_response(item) for item in result]
    response = StreamingResponse(**export_to_file(result, type_file))
    filename = "invoice"
    if client_id:
        filename += f"_client_{client_id}"
    filename += f"_{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.{type_file}"
    return response

@invoice.get("/invoice_item", response_model=PaginationResponse[InvoiceItemResponse])
async def list_invoice_item(user: GetActiveUserDep, pagin: PaginDep, params: Annotated[ReportRequest, Depends()] = None):
    auow = payment_injector.get(AbstractUnitOfWork)
    pagin = InvoiceRequestMapper.to_pagin_params(pagin)
    params = InvoiceRequestMapper.get_items_params(params)
    result = await payment_uc.list_invoice_item(auow, pagin=pagin, params=params)
    return InvoiceResponseMapper.to_paginated_response(result, InvoiceItemResponse)

@invoice.get("/invoice_item/file/{type_file}")
async def get_invoice_file(type_file: str, user: GetActiveUserDep, params: Annotated[ReportRequest, Depends()] = None):
    auow = payment_injector.get(AbstractUnitOfWork)
    params = InvoiceRequestMapper.get_items_params(params)
    try:
        result = await payment_uc.list_invoice_item(auow, params=params, pagin=None)
        result = InvoiceResponseMapper.to_list_response(result, InvoiceItemReportResponse)
        response = StreamingResponse(**export_to_file(result, type_file, exclude=["payment_info"]))
        filename_parts = ["invoice_item"]
        if params:
            for key, value in params.__dict__.items():
                if value:
                    filename_parts.append(f"{key}_{value}")
        filename_parts.append(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        filename = "_".join(filename_parts)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.{type_file}"
        return response
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
@invoice.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(invoice_id: Annotated[UUID, Path()], user: GetActiveUserDep): 
    auow = payment_injector.get(AbstractUnitOfWork)
    result, status = await payment_uc.get_invoice(auow, invoice_id)
    return InvoiceResponseMapper.to_detail_response(result, status)



