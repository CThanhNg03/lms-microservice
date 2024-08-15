from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

from app.model.base import PyObjectId
from app.model import Conversation, Message

class ConversationList(BaseModel):
    conversations: List[Conversation]

class NewMessage(BaseModel):
    senderID: int
    conversationID: str
    content: str
    readBy: List[int] = []
    replyTo: Optional[str] = None

class NewConversation(BaseModel):
    members: List[int]
    title: Optional[str] = ""

class ConversationResponse(Conversation):
    latestMessage: Message | None
    latestTimeChat: datetime | None
    