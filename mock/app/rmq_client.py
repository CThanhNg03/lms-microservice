import asyncio
import json
import uuid
from typing import MutableMapping
from aio_pika import connect, Message, exceptions
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue, AbstractIncomingMessage

from app.setting import env
from app import logger

class RMQClient:
    connection: AbstractConnection | None = None
    channel: AbstractChannel | None = None
    callback_queue: AbstractQueue | None = None

    def __init__(self, retry=5, delay=5) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.retry = retry
        self.delay = delay
        pass
        
    async def connect(self):
        attemp = 0
        while attemp < self.retry:
            try:
                self.connection = await connect(env.RMQ_URL)
                self.channel = await self.connection.channel()
                self.callback_queue = await self.channel.declare_queue(exclusive=True)
                await self.callback_queue.consume(self.on_response, no_ack=True)
                return self
            except (exceptions.AMQPConnectionError, ConnectionRefusedError) as e:
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
        pass

    async def disconnect(self):
        if self.connection is None:
            return
        await self.connection.close()
        logger.info("Disconnected from RabbitMQ")
        pass

    async def on_response(self, message: AbstractIncomingMessage):
        if message.correlation_id is None:
            logger.error("Received message without correlation_id")
            return
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)
        pass

    async def call(self, data, routing):
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        self.futures[correlation_id] = future
        logger.info(f"Sending message: {data}")
        await self.channel.default_exchange.publish(
            Message(
                json.dumps(data).encode(),
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=f"{routing}",
        )
        return await future
        pass

    
    async def get_report(self, data):
        return await self.call(data, "report")
    
    async def get_order(self, data):
        return await self.call(data, "order")
    
rmqClient = RMQClient()
