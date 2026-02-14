from pydantic import BaseModel, UUID4
from typing import Optional, Dict, Any


class EventSchema(BaseModel):
    user_id: UUID4
    event_type: str
    message: str
    payload: Optional[Dict[str, Any]] = None
