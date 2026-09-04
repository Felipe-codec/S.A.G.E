from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RedemptionInfoResponse(BaseModel):
    valid: bool
    steam_username: str
    display_name: Optional[str] = None
    expires_at: datetime
    remaining_uses: int
    message: Optional[str] = None


class CodeRequestPayload(BaseModel):
    session_id: Optional[str] = None


class CodeResponse(BaseModel):
    success: bool
    code: Optional[str] = None
    message: str
    expires_in_seconds: int = 60
    search_duration_ms: int = 0
