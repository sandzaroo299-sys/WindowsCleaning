from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RegisterRequest(BaseModel):
    telegram_id: int
    full_name: Optional[str] = None
    building_id: int
    apartment_number: str
    entrance: Optional[int] = 1
    window_side: Optional[str] = "unknown"

class CreateRequest(BaseModel):
    telegram_id: int
    service_type: str  # windows, balcony, both
    comment: Optional[str] = None
    apartment_id: int

class ComplaintRequest(BaseModel):
    telegram_id: int
    request_id: int
    description: str

class StatusUpdate(BaseModel):
    telegram_id: int
    request_id: int
    new_status: str

class CommentAdd(BaseModel):
    telegram_id: int
    request_id: int
    text: str
    