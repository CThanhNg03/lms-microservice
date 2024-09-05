from functools import wraps
import json
from typing import Callable, List
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage, AbstractConnection, AbstractChannel
from aio_pika.exceptions import AMQPConnectionError
import asyncio

from app.setting.setting import logger, settings

class RMQService:
    """
    A class to manage the RabbitMQ service as RPC server's route.
    """
    queues = dict()
    
    def __init__(self, retry: int=5, delay: int=5):
        self.connection: AbstractConnection = None
        self.channel: AbstractChannel = None
        self.retry = retry
        self.delay = delay

    async def connect(self, queue_name: str):
        attemp = 0
        while attemp < self.retry:
            try:
                self.connection = await connect(settings.RMQ_URL)
                self.channel = await self.connection.channel()
                queue = await self.channel.declare_queue(queue_name)
                await queue.consume(self.queues[queue_name])
                logger.info(f"Application consume on queue: {queue_name}")
                return self
            except (AMQPConnectionError, ConnectionRefusedError) as e:
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

    def _wrap_func(self, func, callback, queue_name):
        if queue_name not in self.queues:
            self.queues[queue_name] = callback

        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorate
    
    def rpc(self, func: Callable=None, *, queue_name=None):
        """
        Decorator to create a callback queue.
        Args:
            queue_name: The name of the queue.
        """
        if func is None:
            return lambda f: self.rpc(f, queue_name=queue_name)
        async def process_message(message: AbstractIncomingMessage):
            async with message.process():
                data = json.loads(message.body)
                logger.info(f"Received message on queue {queue_name}: {data}")
                try:
                    request_type = func.__annotations__["body"]
                    message.body = request_type(**data)
                    response = await func(message.body)
                except Exception as e:
                    logger.error(f"Failed to process queue {queue_name}: {e}")
                    response = {
                        "status": False,
                        "message": str(e)
                    }
                
                await self.channel.default_exchange.publish(
                    message=Message(
                        body=json.dumps(response).encode(),
                        correlation_id=message.correlation_id
                    ),
                    routing_key=message.reply_to
                )
                status = "Success" if response["status"] else "Failed"
                logger.info(f"Response for queue: {queue_name} - {status}")

        return self._wrap_func(func, process_message, queue_name)
    
    async def run(self):
        loop = asyncio.get_event_loop()
        tasks = []
        for queue in self.queues:
            task = loop.create_task(self.connect(queue))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def close(self):
        await self.connection.close()

class RMQApp:
    """
    A class to manage RMQService instances.
    """
    def __init__(self):
        self.services: List[RMQService] = []

    def include(self, service: RMQService):
        self.services.append(service)
    
    async def start(self):
        tasks = [service.run() for service in self.services]
        await asyncio.gather(*tasks)

    async def stop(self):
        tasks = [service.close() for service in self.services]
        await asyncio.gather(*tasks)
