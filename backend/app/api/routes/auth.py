from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_seller
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.seller import Seller
from app.schemas.auth import SellerLogin, SellerOut, SellerRegister, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=SellerOut, status_code=status.HTTP_201_CREATED)
def register(payload: SellerRegister, db: Session = Depends(get_db)):
    """Cadastra um novo revendedor no sistema."""
    existing = db.query(Seller).filter(Seller.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma conta cadastrada com este e-mail.",
        )

    hashed_pwd = hash_password(payload.password)
    seller = Seller(email=payload.email, hashed_password=hashed_pwd)
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return seller


@router.post("/login", response_model=TokenResponse)
def login(payload: SellerLogin, response: Response, db: Session = Depends(get_db)):
    """
    Autentica o revendedor e emite token JWT.
    Injeta cookie HttpOnly e Secure (em produção) com SameSite=None para compatibilidade Vercel <-> Render.
    """
    seller = db.query(Seller).filter(Seller.email == payload.email).first()
    if not seller or not verify_password(payload.password, seller.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Conta de revendedor inativa."
        )

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=seller.id, expires_delta=expires_delta)

    # Configuração de cookies seguros para produção cross-site (Vercel <-> Render)
    is_prod = settings.APP_ENV == "production"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        seller=SellerOut.model_validate(seller),
    )


@router.get("/me", response_model=SellerOut)
def get_me(current_seller: Seller = Depends(get_current_seller)):
    """Retorna os dados do revendedor atualmente autenticado."""
    return current_seller


@router.post("/logout")
def logout(response: Response):
    """Limpa os cookies de autenticação do revendedor."""
    is_prod = settings.APP_ENV == "production"
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
    )
    return {"message": "Sessão encerrada com sucesso."}
