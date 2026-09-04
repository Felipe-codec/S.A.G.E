from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_seller
from app.db.session import get_db
from app.models.seller import Seller
from app.models.steam_account import SteamAccount
from app.schemas.steam_account import SteamAccountCreate, SteamAccountOut, SteamAccountUpdate

router = APIRouter(prefix="/api/v1/steam-accounts", tags=["Steam Accounts"])


@router.get("", response_model=List[SteamAccountOut])
def list_steam_accounts(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Lista todas as contas Steam cadastradas pelo revendedor."""
    return (
        db.query(SteamAccount)
        .filter(SteamAccount.seller_id == current_seller.id)
        .order_by(SteamAccount.created_at.desc())
        .all()
    )


@router.post("", response_model=SteamAccountOut, status_code=status.HTTP_201_CREATED)
def create_steam_account(
    payload: SteamAccountCreate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Cadastra uma nova conta Steam para gerenciamento e resgate de códigos."""
    existing = (
        db.query(SteamAccount)
        .filter(
            SteamAccount.seller_id == current_seller.id,
            SteamAccount.username == payload.username.strip(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já cadastrou uma conta Steam com este usuário.",
        )

    account = SteamAccount(
        seller_id=current_seller.id,
        username=payload.username.strip(),
        display_name=payload.display_name,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/{account_id}", response_model=SteamAccountOut)
def update_steam_account(
    account_id: int,
    payload: SteamAccountUpdate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Atualiza dados de uma conta Steam existente."""
    account = (
        db.query(SteamAccount)
        .filter(SteamAccount.id == account_id, SteamAccount.seller_id == current_seller.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conta Steam não encontrada."
        )

    if payload.display_name is not None:
        account.display_name = payload.display_name
    if payload.is_active is not None:
        account.is_active = payload.is_active

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_steam_account(
    account_id: int,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Remove uma conta Steam do catálogo do revendedor."""
    account = (
        db.query(SteamAccount)
        .filter(SteamAccount.id == account_id, SteamAccount.seller_id == current_seller.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conta Steam não encontrada."
        )

    db.delete(account)
    db.commit()
    return None
