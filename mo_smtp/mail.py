# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from datetime import datetime
from datetime import timedelta
from email.message import EmailMessage
import aiosmtplib
from .config import SMTPSecurity

import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from mo_smtp.models import ManagerNotification
from mo_smtp import depends
from mo_smtp.utils import email_builders

logger = structlog.get_logger()


class EmailClient:
    def __init__(self, settings):
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_security = settings.smtp_security
        self.sender = settings.sender
        self.dry_run = settings.dry_run

    async def send_email(self, message: EmailMessage):
        if self.dry_run:
            logger.info("Dry run: email not sent", subject=message["Subject"])
            return

        use_tls = self.smtp_security is SMTPSecurity.TLS
        smtp = aiosmtplib.SMTP(
            hostname=self.smtp_host, port=self.smtp_port, use_tls=use_tls
        )
        await smtp.connect()
        if self.smtp_user and self.smtp_password:
            await smtp.login(self.smtp_user, self.smtp_password)

        await smtp.send_message(message)
        await smtp.quit()
        logger.info("Email sent", subject=message["Subject"], to=message["To"])


class EmailAlert:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        email_client: EmailClient,
        mo: depends.GraphQLClient,
        interval: int,
        pre_notification_days: int,
    ):
        self.sessionmaker = sessionmaker
        self.email_client = email_client
        self.mo = (mo,)
        self.interval = interval
        self.pre_notification_days = pre_notification_days
        self.event = asyncio.Event()

    async def _background(self) -> None:
        while True:
            try:
                now = datetime.utcnow()
                pre_threshold = now + timedelta(days=self.pre_notification_days)

                async with self.sessionmaker() as session, session.begin():
                    # Pre notifications
                    pre_stmt = select(ManagerNotification).where(
                        ManagerNotification.pre_notification_sent == False,
                        ManagerNotification.end_date <= pre_threshold,
                        ManagerNotification.end_date > now,
                    )
                    pre_notifications = (
                        (await session.execute(pre_stmt)).scalars().all()
                    )

                    for n in pre_notifications:
                        try:
                            msg = await email_builders.build_manager_email(n, self.mo)
                            await self.email_client.send_email(msg)
                            n.pre_notification_sent = True
                            logger.info(
                                "Pre-notification sent", employee=n.employee_uuid
                            )
                        except Exception as e:
                            logger.exception(
                                "Failed to send pre-notification",
                                employee=n.employee_uuid,
                                error=e,
                            )

                    # # Main notifications
                    # main_stmt = select(ManagerNotification).where(
                    #     ManagerNotification.notification_sent == False,
                    #     ManagerNotification.end_date <= now,
                    #     ManagerNotification.pre_notification_sent == True,
                    # )
                    # main_notifications = (await session.execute(main_stmt)).scalars().all()
                    #
                    # for n in main_notifications:
                    #     try:
                    #         msg = await email_builders.build_manager_email(n, depends.GraphQLClient)
                    #         await self.email_client.send_email(msg)
                    #         n.notification_sent = True
                    #         await session.delete(n)
                    #         logger.info("Main notification sent", employee=n.employee_uuid)
                    #     except Exception as e:
                    #         logger.exception("Failed to send main notification", employee=n.employee_uuid, error=e)

            except Exception as e:
                logger.exception("Error in background email loop", error=e)

            await asyncio.sleep(self.interval)

    def start(self):
        asyncio.create_task(self._background())
        logger.info("EmailAlert background task started")
