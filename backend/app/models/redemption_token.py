from datetime import datetime, timezone
from typing import List
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class RedemptionToken(Base):
    __tablename__ = "redemption_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    steam_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("steam_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Hash SHA-256 do token gerado para consulta sem armazenar texto puro
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    steam_account: Mapped["SteamAccount"] = relationship("SteamAccount", back_populates="tokens")
    seller: Mapped["Seller"] = relationship("Seller", back_populates="tokens")
    sessions: Mapped[List["RedemptionSession"]] = relationship(
        "RedemptionSession", back_populates="token", cascade="all, delete-orphan"
    )
    code_requests: Mapped[List["CodeRequest"]] = relationship(
        "CodeRequest", back_populates="token", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_redemption_tokens_account_expires", "steam_account_id", "expires_at"),
    )
