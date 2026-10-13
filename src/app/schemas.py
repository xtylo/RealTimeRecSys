from typing import Literal

from pydantic import BaseModel

EventType = Literal["view", "cart", "purchase"]


class Event(BaseModel):
    session_id: str
    product_id: int
    event_type: EventType


class Recommendation(BaseModel):
    product_id: int
    score: float
