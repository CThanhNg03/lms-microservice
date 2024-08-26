import logging
import asyncio
from typing import Annotated, List
from fastapi import FastAPI, UploadFile, WebSocket, HTTPException, Depends, WebSocketDisconnect
import json
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer

import app.services.crud as crud
from app.services.rmqclient import rmqClient
import app.schema as schema
from app.services.wsmanager import connection_manager as manager

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await rmqClient.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rmqClient.disconnect()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauthDep = Annotated[str, Depends(oauth2_scheme)]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(log_format)
logger.addHandler(stream_handler)

logger.info("This is a debug message")

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str, token: str):
    user_id = await rmqClient.get_current_user(token)
    if user_id is None:
        await websocket.close()
        raise HTTPException(status_code=403, detail="Forbidden")
    user_id = int(user_id)
    conversation = await crud.get_conversation(conversation_id)
    if conversation is None:
        await websocket.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
    if user_id not in conversation.members:
        await websocket.close()
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await manager.connect(websocket, conversation_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data["type"]=="read_receipt":
                await manager.broadcast_read_receipt(conversation_id, data["message_id"], user_id)
                asyncio.ensure_future(crud.update_message_read_by(data["message_id"], user_id))
            elif data["type"]=="reaction":
                await manager.broadcast(conversation_id, data)
                asyncio.ensure_future(crud.update_message_reactions(data["react_to"], data["react_by"], data["reaction"]))
            else:
                await manager.broadcast_except(conversation_id, data, user_id, conversation.members)
                message = schema.NewMessage(senderID=user_id, content=data['content'], conversationID=conversation_id)
                if data.get("replyTo"):
                    message.replyTo = data["replyTo"]
                asyncio.ensure_future(crud.store_new_message(message))
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        await manager.broadcast(conversation_id, {"type": "user_leave", "user_id": user_id})
        pass
    
@app.websocket("/noti")
async def noti_endpoint(websocket: WebSocket, token: str):
    user_id = await rmqClient.get_current_user(token)
    if user_id is None:
        await websocket.close()
        raise HTTPException(status_code=403, detail="Forbidden")
    user_id = int(user_id)
    await manager.noti_connect(websocket, user_id)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.noti_disconnect(user_id)
        pass

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, token: oauthDep):
    user_id = await rmqClient.get_current_user(token)
    result = await crud.get_conversation(conversation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if int(user_id) not in result.members:
        raise HTTPException(status_code=403, detail="Forbidden")
    return result

@app.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str, timestamp: str, token: oauthDep):
    user_id = await rmqClient.get_current_user(token)
    result = await crud.get_conversation(conversation_id)
    if result is None:
        return HTTPException(status_code=404, detail="Conversation not found")
    if int(user_id) not in result.members:
        return HTTPException(status_code=403, detail="Forbidden")
    return await crud.get_messages(conversation_id=conversation_id, timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f"))

@app.post("/conversation",
          response_model=schema.Conversation,
          response_model_by_alias=False,
          status_code=201
          )
async def create_conversation(conversation: schema.NewConversation, token: oauthDep):
    user_id = await rmqClient.get_current_user(token)
    if int(user_id) not in conversation.members:
        conversation.members.append(user_id)
    return await crud.create_conversation(schema.Conversation(**conversation.dict(), createdAt=datetime.now()))

@app.get("/my_conversations")
async def get_my_conversations(token: oauthDep):
    user_id = await rmqClient.get_current_user(token)
    return await crud.get_my_conversations(int(user_id))

@app.get("/my_recent_chat")
async def get_my_recent_chat(token: oauthDep, limit: int = 30) -> List[int]:
    user_id = await rmqClient.get_current_user(token)
    return await crud.get_my_recent_chat(int(user_id), limit) 

@app.post("/new_direct_message")
async def new_direct_message(conversation: schema.NewConversation, token: oauthDep):
    user_id = await rmqClient.get_current_user(token)
    if int(user_id) not in conversation.members:
        conversation.members.append(int(user_id))
    return await crud.get_or_create_dm(conversation)

@app.post("/send_file")
async def send_file(file: UploadFile):
    return {"filename": file.filename}

