from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ImapConfigCreate(BaseModel):
    host: str = Field(..., json_schema_extra={"example": "imap.gmail.com"})
    port: int = Field(default=993, ge=1, le=65535)
    username: str = Field(..., json_schema_extra={"example": "revendedor@gmail.com"})
    password: str = Field(..., min_length=1, description="Senha IMAP ou App Password (criptografada em repouso)")
    use_ssl: bool = Field(default=True)


class ImapConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    host: str
    port: int
    username: str
    use_ssl: bool
    created_at: datetime
    updated_at: datetime
    # ATENÇÃO: Nunca retornar 'password' ou 'encrypted_password' na API pública


class ImapTestRequest(BaseModel):
    host: str
    port: int = 993
    username: str
    password: Optional[str] = None  # Se omitido, usa a senha já salva do revendedor
    use_ssl: bool = True


class ImapTestResponse(BaseModel):
    success: bool
    message: str
    response_time_ms: int
