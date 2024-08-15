from pydantic import BaseModel
from typing import Dict, Optional, List
from pydantic import ConfigDict, BaseModel, Field
from bson import ObjectId
from datetime import datetime

from app.model.base import PyObjectId

class Message(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    senderID: int = Field(...)
    conversationID: str = Field(...)
    content: str = Field(...)
    timestamp: datetime = Field(...)
    readBy: List[int] = Field(...)
    reactions: Optional[List[Dict[int, str]]] = None
    replyTo: Optional[str] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
