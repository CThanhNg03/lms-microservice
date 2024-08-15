from datetime import datetime
from pymongo import ReturnDocument
from bson import ObjectId

from app.model import Message, Conversation
from app.core.db import message_collection, conversation_collection
from app.schema import NewMessage, ConversationResponse, ConversationList, NewConversation

async def create_conversation(conversation: Conversation) -> Conversation:
    result = await conversation_collection.insert_one(conversation.model_dump(by_alias=True, exclude=['id']))
    created_conv = await conversation_collection.find_one({'_id': ObjectId(result.inserted_id)})
    return Conversation(**created_conv)

async def get_conversation(conversation_id: int) -> ConversationResponse:
    result = await conversation_collection.find_one({'_id': ObjectId(conversation_id)})
    if result is None:
        return None
    last_message = await message_collection.find_one({'conversationID': str(conversation_id)}, sort=[('timestamp', -1)])
    if last_message is None:
        return ConversationResponse(**result, latestMessage=None, latestTimeChat=None)
    return ConversationResponse(**result, latestMessage=Message(**last_message), latestTimeChat=last_message['timestamp'])

async def store_new_message(message: NewMessage) -> Message:
    message = Message(**message.model_dump(), timestamp=datetime.now())
    result = await message_collection.insert_one(message.model_dump())
    await conversation_collection.find_one_and_update(
        {'_id': ObjectId(message.conversationID)},
        {'$set': {'lastChat': message.timestamp}},
        return_document=ReturnDocument.AFTER
    )
    return result

async def update_message_read_by(message_id: int, user_id: int) -> None:
    result = await message_collection.find_one_and_update(
        {'_id': ObjectId(message_id)},
        {'$addToSet': {'readBy': user_id}},
        return_document=ReturnDocument.AFTER
    )
    if result is None:
        raise Exception('Message not found')
    return None

async def update_message_reactions(message_id: int, user_id: int, reaction: str) -> None:
    result = await message_collection.find_one_and_update(
        {'_id': ObjectId(message_id)},
        {'$push': {'reactions': {user_id: reaction}}},
        return_document=ReturnDocument.AFTER
    )
    if result is None:
        raise Exception('Message not found')
    return None

async def get_messages(*, conversation_id: str, timestamp: datetime, limit: int = 20) -> list[Message]:
    result = await message_collection.find({'conversationID': conversation_id, 'timestamp': {'$gt': timestamp}}).sort('timestamp', -1).limit(limit).to_list(length=limit)
    return [Message(**msg) for msg in result]

async def get_my_conversations(user_id: int) -> ConversationList:
    result = await conversation_collection.find({'members': user_id}).to_list(length=100)
    return [Conversation(**conv) for conv in result]

async def get_my_recent_chat(user_id: int, limit: int = 30) -> list[int]:
    result = await conversation_collection.find({'members': user_id}, sort=[('lastChat', -1)]).limit(limit).to_list(length=limit)
    recent_chat_to = set()
    for conv in result:
        recent_chat_to.update(conv['members'])
    return list(recent_chat_to)

async def get_or_create_dm(conversation: NewConversation) -> Conversation:
    result = await conversation_collection.find_one({'members': {'$all': conversation.members, '$size': 2}})
    if result is not None:
        return Conversation(**result)
    return await create_conversation(Conversation(**conversation.model_dump(), createdAt=datetime.now()))