import asyncio
from asyncio import tasks
from typing import Dict
from aio_pika import connect
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
import logging
import json

from app.core import env, logger
from app.schema import NewInvoice, NewOrder, ReportRequest
from app.service import crud
from app.service.pay_gateway import paymentGateway
from app.model import InvoiceStatus

class RMQServer:
    def __init__(self, queue, retry = 5, delay=5) -> None:
        self.connection = None
        self.channel = None
        self.processes = {
            "order": (self.process_order, NewOrder),
            "report": (self.process_report, ReportRequest),
        }
        self.queue = queue
        self.retry = retry
        self.delay = delay

    async def connect(self, queue):
        attemp = 0
        while attemp < self.retry:
            try:
                self.connection = await connect(env.RMQ_URL)
                self.channel = await self.connection.channel()
                self.queue = await self.channel.declare_queue(queue)
                self.process = self.processes[queue][0]
                self.request = self.processes[queue][1]
                await self.queue.consume(self.on_request, no_ack=False)
                return self
            except (aio_pika.exceptions.AMQPConnectionError, ConnectionRefusedError) as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                attemp += 1
                if attemp < self.retry:
                    await asyncio.sleep(self.delay)
                    logger.info(f"Retrying to connect to RabbitMQ: {attemp}")
                else:
                    logger.error(f"Failed to connect to RabbitMQ: {e}")
                    raise e
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise e
    
    async def on_request(self, message: AbstractIncomingMessage):
        async with message.process():
            data = json.loads(message.body)
            logger.info(f"Received message: {data}")
            try:
                data = self.request(**data)
                response = await self.process(data)
                logger.debug(f"Response: {response}")
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
                response = {"error": str(e)}
            
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=message.correlation_id,
                ),
                routing_key=message.reply_to,
            )
    
    async def process_order(self, data: NewOrder):
        newInvoice = NewInvoice(**data.model_dump(exclude={"items"}))
        logger.info(f"Processing order: {newInvoice}")
        invoice_id = await crud.create_invoice(invoice=newInvoice, items=data.items)
        transaction = await crud.get_transaction(invoice_id=invoice_id)
        result = await paymentGateway.process_payment(transaction=transaction)
        if result.get("status"):
            await crud.update_invoice_status(invoice_id=invoice_id, status=InvoiceStatus.PAID)
        return result
        pass
    
    async def process_report(self, data: ReportRequest):
        result = await crud.get_report(request=data)
        result = [r.__dict__ for r in result]
        for r in result:
            r.pop("_sa_instance_state")
            r["invoice_id"] = str(r["invoice_id"])
        return result
        pass
    
    async def run(self):
        loop = asyncio.get_running_loop()
        task = loop.create_task(self.connect(self.queue))
        await task     

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")