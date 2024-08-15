import motor.motor_asyncio

from app.core.setting import env

client = motor.motor_asyncio.AsyncIOMotorClient(env.DATABASE_URL)

database = client.get_database("lms")

message_collection = database.get_collection("message")

conversation_collection = database.get_collection("conversation")
