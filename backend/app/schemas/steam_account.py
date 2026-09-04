from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SteamAccountCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=100, description="Login da conta Steam")
    display_name: Optional[str] = Field(None, max_length=100, description="Apelido / Descrição amigável")


class SteamAccountUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None


class SteamAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    username: str
    display_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
