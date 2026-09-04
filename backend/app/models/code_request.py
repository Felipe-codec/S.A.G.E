from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CodeRequest(Base):
    __tablename__ = "code_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    steam_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("steam_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("redemption_tokens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # SUCCESS, TIMEOUT, IMAP_ERROR, NOT_FOUND
    code_found_masked: Mapped[str] = mapped_column(String(10), nullable=True)  # ex: ***42 (NUNCA texto puro)
    search_duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    steam_account: Mapped["SteamAccount"] = relationship("SteamAccount", back_populates="code_requests")
    token: Mapped["RedemptionToken"] = relationship("RedemptionToken", back_populates="code_requests")

    __table_args__ = (
        Index("ix_code_requests_account_requested", "steam_account_id", "requested_at"),
    )
