from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SellerRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Senha de acesso do revendedor")


class SellerLogin(BaseModel):
    email: EmailStr
    password: str


class SellerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    seller: SellerOut
