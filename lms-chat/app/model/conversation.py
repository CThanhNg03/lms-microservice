from pydantic import BaseModel
from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field
from bson import ObjectId
from datetime import datetime

from app.model.base import PyObjectId

class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    members: List[int] = Field(...)
    createdAt: datetime = Field(...)
    title: str = Field(...)
    lastChat: Optional[datetime] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )