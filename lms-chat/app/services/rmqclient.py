import asyncio
import uuid
from typing import MutableMapping
from aio_pika import connect, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue, AbstractIncomingMessage
import logging

from app.core.setting import env

class RMQClient:
    connection: AbstractConnection | None = None
    channel: AbstractChannel | None = None
    callback_queue: AbstractQueue | None = None

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        pass
        
    async def connect(self):
        try:
            self.connection = await connect(env.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.callback_queue = await self.channel.declare_queue(exclusive=True)
            await self.callback_queue.consume(self.on_response, no_ack=True)
            logging.info("Connected to RabbitMQ")
            return self
        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
        pass

    async def disconnect(self):
        if self.connection is None:
            return
        await self.connection.close()
        logging.info("Disconnected from RabbitMQ")
        pass

    async def on_response(self, message: AbstractIncomingMessage):
        if message.correlation_id is None:
            logging.error("Received message without correlation_id")
            return
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)
        pass

    async def call(self, data, routing):
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                str(data).encode(),
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=f"{routing}",
        )
        return await future
        pass

    
    async def get_current_user(self, token: str):
        # return self.call(token, 'get_current_user')
        asyncio.sleep(1)
        try:
            return token[:3]
        except:
            return None
    
rmqClient = RMQClient()
