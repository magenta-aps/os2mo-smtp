from datetime import datetime
from uuid import UUID

from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class SentAlert(Base):
    """Track sent alerts to avoid sending duplicate emails.

    Used by both the relation alert (org_unit) and the rolebinding alert (ituser).
    The alert_type distinguishes between them, and content_hash allows detecting
    when the message content has changed (relevant for rolebinding alerts)."""

    __tablename__ = "sent_alert"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(50))
    object_uuid: Mapped[UUID]
    content_hash: Mapped[str | None] = mapped_column(String(64))
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now())
