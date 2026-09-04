from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TokenGenerateRequest(BaseModel):
    steam_account_id: int
    expires_in_seconds: Optional[int] = Field(default=3600, ge=60, le=86400 * 30)
    max_uses: Optional[int] = Field(default=1, ge=1, le=10)


class TokenGenerateResponse(BaseModel):
    id: int
    token: str  # Retornado apenas uma única vez na geração
    token_url: str
    steam_account_id: int
    steam_username: str
    expires_at: datetime
    max_uses: int


class TokenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    steam_account_id: int
    token_hash_masked: str
    max_uses: int
    current_uses: int
    expires_at: datetime
    is_active: bool
    created_at: datetime
