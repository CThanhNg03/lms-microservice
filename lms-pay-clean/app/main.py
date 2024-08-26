from fastapi import FastAPI

from app.endpoint.rpc.rmq_service import RMQApp
from app.endpoint.rpc.rpc import rabbit


class PayApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rmq = RMQApp()

app = PayApp()

app.rmq.include(rabbit)

@app.on_event("startup")
async def startup_event():
    await app.rmq.start()

@app.on_event("shutdown")
async def shutdown_event():
    await app.rmq.stop()