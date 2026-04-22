from pydantic import BaseModel, Field
from typing import Optional, Literal, List

LanguageCode = Literal['en', 'hi', 'ta']

class SessionState(BaseModel):
    session_id: str
    patient_id: str
    language: LanguageCode = 'en'
    intent: str = 'unknown'
    pending_confirmation: bool = False
    selected_slot_id: Optional[str] = None
    selected_hold_id: Optional[str] = None
    selected_appointment_id: Optional[str] = None
    last_agent_message: Optional[str] = None
    trace: List[dict] = Field(default_factory=list)