from uuid import UUID
from enum import Enum

from fastramqpi.config import Settings as FastRAMQPISettings
from fastramqpi.ramqp.config import AMQPConnectionSettings
from pydantic import BaseSettings
from pydantic import PositiveInt


class SmtpAMQPConnectionSettings(AMQPConnectionSettings):
    queue_prefix = "smtp"
    prefetch_count = 1  # MO cannot handle too many requests


class SmtpFastRAMQPISettings(FastRAMQPISettings):
    amqp: SmtpAMQPConnectionSettings
    mo_graphql_version: PositiveInt = 25


class SMTPSecurity(Enum):
    NONE = "none"
    STARTTLS = "starttls"
    TLS = "tls"


class EmailSettings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    smtp_user: str | None = None
    smtp_password: str | None = None
    sender: str = "os2mo@magenta.dk"
    smtp_port: int = 465
    smtp_host: str = "mailcatcher"
    smtp_security: SMTPSecurity
    dry_run: bool = False
    # Remove this?
    receiver_override: str = ""


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: SmtpFastRAMQPISettings

    active_agents: list[str] = []
    receivers: list[str] = []
    root_loen_org: UUID | None = None
    alert_manager_removal_use_org_unit_emails: bool = False

    email_settings: EmailSettings
