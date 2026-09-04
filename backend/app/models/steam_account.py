from datetime import datetime, timezone
from typing import List
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SteamAccount(Base):
    __tablename__ = "steam_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    seller: Mapped["Seller"] = relationship("Seller", back_populates="steam_accounts")
    tokens: Mapped[List["RedemptionToken"]] = relationship(
        "RedemptionToken", back_populates="steam_account", cascade="all, delete-orphan"
    )
    code_requests: Mapped[List["CodeRequest"]] = relationship(
        "CodeRequest", back_populates="steam_account", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_steam_accounts_seller_username", "seller_id", "username"),
    )
