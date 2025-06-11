from uuid import UUID
from enum import Enum

from fastramqpi.config import Settings as FastRAMQPISettings
from fastramqpi.ramqp.config import AMQPConnectionSettings
from pydantic import BaseSettings
from pydantic import Field
from pydantic import PositiveInt


class SmtpAMQPConnectionSettings(AMQPConnectionSettings):
    queue_prefix = "smtp"
    prefetch_count = 1  # MO cannot handle too many requests


class SmtpFastRAMQPISettings(FastRAMQPISettings):
    amqp: SmtpAMQPConnectionSettings
    mo_graphql_version: PositiveInt = 22


class SMTPSecurity(Enum):
    NONE = "none"
    STARTTLS = "starttls"
    TLS = "tls"


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: SmtpFastRAMQPISettings

    application_name: str = "os2mo_email_listener"

    active_agents: list[str] = Field(
        [], description="Agents which are actively listening and sending mails"
    )
    root_loen_org: UUID | None = None
    alert_manager_removal_use_org_unit_emails: bool = False


class EmailSettings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    smtp_user: str | None = Field(None, description="SMTP user")
    smtp_password: str | None = Field(None, description="SMTP password")
    sender: str = "os2mo@magenta.dk"
    smtp_port: int = Field(..., description="SMTP port")
    smtp_host: str = Field(..., description="SMTP host. For example 'smtp.gmail.com' ")
    smtp_security: SMTPSecurity
    dry_run: bool = Field(
        False,
        description="When True, will print mails to the console but not send anything",
    )
    receiver_override: str = Field(
        "",
        description=(
            "Set to an email address to always send mails to this address. "
            "Useful for testing purposes."
        ),
    )
    receivers: list[str] = Field([], description="Email addresses to send mail to")
