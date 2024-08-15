# import aioredis

# from app.core.setting import env

# class RedisService:
#     def __init__(self):
#         self.redis = aioredis.from_url(env.REDIS_URL)
    
#     async def get(self, key: str):
#         return await self.redis.get(key)
    
#     async def set(self, key: str, value: str):
#         await self.redis.set(key, value)

#     async def delete(self, key: str):
#         await self.redis.delete(key)
        
#     async def publish(self, channel: str, message: str):
#         await self.redis.publish(channel, message)

#     async def subscribe(self, channel: str):
#         return await self.redis.subscribe(channel)

# redisService = RedisService()
    