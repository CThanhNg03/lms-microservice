from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse

from app.common.dependencies.auth import GetActiveUserDep
from app.common.dependencies.pagination import PaginDep
from app.common.utils.export import export_to_file
from app.endpoint.schema.invoice import InvoiceItemResponse, InvoiceResponse, PaginationResponse, ReportRequest
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
    pagin = PaginationParamsModel(**pagin)
    params = GetInvoiceParamsModel(client_id=client_id) if client_id else None
    result = await payment_uc.list_invoice(auow, params=params, pagin=pagin)
    return PaginationResponse[InvoiceResponse](**result.__dict__)

@invoice.get("/file/{type_file}")
async def get_invoice_file(type_file: str, user: GetActiveUserDep, client_id: Optional[int] = None):
    auow = payment_injector.get(AbstractUnitOfWork)
    params = GetInvoiceParamsModel(client_id=client_id) if client_id else None
    result = await payment_uc.list_invoice(auow, params=params, pagin=None)
    result = [InvoiceResponse(**item.__dict__) for item in result]
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
    pagin = PaginationParamsModel(**pagin)
    params = GetInvoiceItemParamsModel(**params.model_dump()) if params else None
    result = await payment_uc.list_invoice_item(auow, pagin=pagin, params=params)
    return PaginationResponse[InvoiceItemResponse](**result.__dict__)

@invoice.get("/invoice_item/file/{type_file}")
async def get_invoice_file(type_file: str, user: GetActiveUserDep, params: Annotated[ReportRequest, Depends()] = None):
    auow = payment_injector.get(AbstractUnitOfWork)
    params = GetInvoiceItemParamsModel(**params.model_dump()) if params else None
    try:
        result = await payment_uc.list_invoice_item(auow, params=params, pagin=None)
        result = [InvoiceItemResponse(**item.__dict__) for item in result]
        response = StreamingResponse(**export_to_file(result, type_file))
        filename_parts = ["invoice_item"]
        if params:
            for key, value in params.__dict__.items():
                if value:
                    filename_parts.append(f"{key}_{value}")
        filename_parts.append(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        filename = "_".join(filename_parts)
        logger.info(f"filename: {filename}")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.{type_file}"
        return response
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
@invoice.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: Annotated[UUID, Path()], user: GetActiveUserDep): 
    auow = payment_injector.get(AbstractUnitOfWork)
    result, status = await payment_uc.get_invoice(auow, invoice_id)
    return InvoiceResponse(**result.__dict__, status=status, id=invoice_id)



