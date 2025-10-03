# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ManagerNotification(Base):
    __tablename__ = "manager_notification"
    id: Mapped[int] = mapped_column(primary_key=True)
    manager_uuid: Mapped[UUID] = mapped_column()
    employee_uuid: Mapped[UUID] = mapped_column()
    org_unit_uuid: Mapped[UUID] = mapped_column()
    end_date: Mapped[datetime] = mapped_column()
    pre_notification_sent: Mapped[bool] = mapped_column(default=False)
    notification_sent: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"ManagerNotification(manager_uuid={self.manager_uuid}, "
            f"employee_uuid={self.employee_uuid}, org_unit_uuid={self.org_unit_uuid}, "
            f"end_date={self.end_date})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ManagerNotification):
            return (
                self.manager_uuid == other.manager_uuid
                and self.end_date == other.end_date
            )
        if other is None:
            return False
        raise NotImplementedError()
