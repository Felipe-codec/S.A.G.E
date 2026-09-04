from typing import Generator, Optional
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.seller import Seller


def get_current_seller(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
) -> Seller:
    """
    Autentica o revendedor.
    Aceita token via Header 'Authorization: Bearer <token>' OU Cookie HttpOnly 'access_token'.
    Isso viabiliza compatibilidade com navegadores que bloqueiam cookies third-party entre Vercel e Render.
    """
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ")[1]
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Forneça o token de acesso.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        seller_id = int(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Subject inválido no token."
        )

    seller = db.query(Seller).filter(Seller.id == seller_id, Seller.is_active == True).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Revendedor não encontrado ou inativo."
        )

    return seller
