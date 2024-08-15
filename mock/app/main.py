from datetime import datetime
import json
import logging
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.rmq_client import rmqClient


class NewPaymentInfo(BaseModel):
    client_id: int
    card_holder: str
    card_number: str
    cvv: str
    exp_date: str
    billing_address: str

class NewInvoice(BaseModel):
    client_id: int
    summary: str
    payment_method: str
    payment_info: Optional[NewPaymentInfo] = None

class NewInvoiceItem(BaseModel):
    course_id: int
    amount: int
    author_id: int

class NewOrder(NewInvoice):
    items: List[NewInvoiceItem]


class ReportRequest(BaseModel):
    start_date: str
    end_date: str
    author_id: int
    course_id: List[int] = []

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await rmqClient.connect()
    logging.info("Connected to RabbitMQ")

@app.on_event("shutdown")
async def shutdown_event():
    await rmqClient.disconnect()

@app.post("/order")
async def test_order(payload: NewOrder):
    message = await rmqClient.get_order(payload.model_dump())
    return json.loads(message)

@app.post("/report")
async def test_report(payload: ReportRequest):
    message = await rmqClient.get_report(payload.model_dump())
    return json.loads(message)