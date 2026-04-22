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

    Two alert types share this table but dedup against different signals
    because their semantics differ:

    alert_type="relation" — see _check_and_alert_org_unit_without_relation.
        The alert reports that an org unit is currently in a bad state
        (no relation to the administrationsorganisation). We want to
        notify once per "entry into bad state", not again until the
        state clears and comes back. The handler therefore:
          * checks for an existing row and skips if present
          * inserts a row when it sends an email
          * deletes the row when the org unit regains a relation, so
            a future removal produces a fresh alert
        content_hash is unused — the message body is fully determined
        by object_uuid.

    alert_type="ituser" — see generate_ituser_email.
        The alert describes the IT user's current roles/itsystem/user_key.
        There is no "state cleared and came back" equivalent; the only
        meaningful reason to re-alert is that the rendered content has
        changed. The handler therefore:
          * hashes the Jinja template context (sha256) into content_hash
          * skips if a row exists with the same content_hash
          * sends and updates the hash (or inserts a new row) otherwise
        No deletion; the row lives forever and records the latest
        content_hash per ituser."""

    __tablename__ = "sent_alert"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(50))
    object_uuid: Mapped[UUID]
    content_hash: Mapped[str | None] = mapped_column(String(64))
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now())
