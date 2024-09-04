from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.endpoint.rpc.rmq_service import RMQApp
from app.endpoint.rpc.rpc import rabbit
from app.endpoint.http.admin import admin
from app.endpoint.http.invoice import invoice
from app.middlewares.exception_handler import ExceptionHandlerMiddlerware
from app.setting.db import initialize_db


class PayApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rmq = RMQApp()

app = PayApp()

app.add_middleware(ExceptionHandlerMiddlerware)

app.rmq.include(rabbit)

app.include_router(admin, prefix="/admin")
app.include_router(invoice, prefix="/invoice")

@app.on_event("startup")
async def startup_event():
    await app.rmq.start()
    await initialize_db()

@app.on_event("shutdown")
async def shutdown_event():
    await app.rmq.stop()