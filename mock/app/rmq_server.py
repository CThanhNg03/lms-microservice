# import aio_pika

# from app.core import env

# class RMQServer:
#     def __init__(self) -> None:
#         pass

#     async def connect(self) -> None:
#         self.connection  = await aio_pika.connect(env.RMQ_URL)
#         self.channel = self.connection.channel()
#         self.exchange = self.channel.default_exchange

#         self.queue = self.channel.declare_queue('rpc_queue')
#         self.queue.consume(self.on_request)
    