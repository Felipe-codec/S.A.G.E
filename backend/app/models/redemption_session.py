from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class RedemptionSession(Base):
    __tablename__ = "redemption_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    token_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("redemption_tokens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_identifier_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    ip_address_masked: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    token: Mapped["RedemptionToken"] = relationship("RedemptionToken", back_populates="sessions")
