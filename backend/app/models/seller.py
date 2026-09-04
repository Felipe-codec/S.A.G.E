from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Seller(Base):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
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

    # Relacionamentos
    imap_configs: Mapped[List["ImapConfig"]] = relationship(
        "ImapConfig", back_populates="seller", cascade="all, delete-orphan"
    )
    steam_accounts: Mapped[List["SteamAccount"]] = relationship(
        "SteamAccount", back_populates="seller", cascade="all, delete-orphan"
    )
    tokens: Mapped[List["RedemptionToken"]] = relationship(
        "RedemptionToken", back_populates="seller", cascade="all, delete-orphan"
    )
    access_logs: Mapped[List["AccessLog"]] = relationship(
        "AccessLog", back_populates="seller", cascade="all, delete-orphan"
    )
