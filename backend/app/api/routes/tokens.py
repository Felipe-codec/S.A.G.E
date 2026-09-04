from datetime import datetime, timedelta, timezone
import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_seller
from app.core.config import settings
from app.core.security import hash_token, mask_token_string
from app.db.session import get_db
from app.models.redemption_token import RedemptionToken
from app.models.seller import Seller
from app.models.steam_account import SteamAccount
from app.schemas.token import TokenGenerateRequest, TokenGenerateResponse, TokenOut

router = APIRouter(prefix="/api/v1/tokens", tags=["Tokens"])


@router.post("/generate", response_model=TokenGenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_redemption_token(
    payload: TokenGenerateRequest,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """
    Gera um novo token de resgate seguro para um cliente final.
    O token em texto plano é retornado apenas nesta resposta para que o revendedor repasse o link.
    No banco de dados, armazena-se exclusivamente o hash SHA-256.
    """
    account = (
        db.query(SteamAccount)
        .filter(SteamAccount.id == payload.steam_account_id, SteamAccount.seller_id == current_seller.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conta Steam não encontrada."
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Conta Steam selecionada está inativa."
        )

    # Gera token criptográfico URL-safe de 32 bytes (43 caracteres base64)
    raw_token = secrets.token_urlsafe(32)
    token_hashed = hash_token(raw_token)

    expires_in = payload.expires_in_seconds or settings.TOKEN_DEFAULT_EXPIRATION
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    token_record = RedemptionToken(
        steam_account_id=account.id,
        seller_id=current_seller.id,
        token_hash=token_hashed,
        max_uses=payload.max_uses or 1,
        current_uses=0,
        expires_at=expires_at,
        is_active=True,
    )
    db.add(token_record)
    db.commit()
    db.refresh(token_record)

    # Constrói o link completo com base na URL do Frontend configurada
    redemption_url = f"{settings.FRONTEND_URL.rstrip('/')}/resgate/{raw_token}"

    return TokenGenerateResponse(
        id=token_record.id,
        token=raw_token,
        token_url=redemption_url,
        steam_account_id=account.id,
        steam_username=account.username,
        expires_at=expires_at,
        max_uses=token_record.max_uses,
    )


@router.get("", response_model=List[TokenOut])
def list_tokens(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Lista os tokens de resgate criados pelo revendedor com hashes mascarados."""
    tokens = (
        db.query(RedemptionToken)
        .filter(RedemptionToken.seller_id == current_seller.id)
        .order_by(RedemptionToken.created_at.desc())
        .limit(100)
        .all()
    )

    output = []
    for t in tokens:
        output.append(
            TokenOut(
                id=t.id,
                steam_account_id=t.steam_account_id,
                token_hash_masked=mask_token_string(t.token_hash),
                max_uses=t.max_uses,
                current_uses=t.current_uses,
                expires_at=t.expires_at,
                is_active=t.is_active,
                created_at=t.created_at,
            )
        )
    return output


@router.post("/{token_id}/revoke")
def revoke_token(
    token_id: int,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Invalida um token de resgate imediatamente."""
    token = (
        db.query(RedemptionToken)
        .filter(RedemptionToken.id == token_id, RedemptionToken.seller_id == current_seller.id)
        .first()
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token não encontrado."
        )

    token.is_active = False
    db.commit()
    return {"message": "Token revogado com sucesso."}
