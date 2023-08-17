from typing import List

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import SecretStr
from ramqp.config import AMQPConnectionSettings


class SmtpAMQPConnectionSettings(AMQPConnectionSettings):
    queue_prefix = "smtp"
    prefetch_count = 1  # MO cannot handle too many requests


class SmtpFastRAMQPISettings(FastRAMQPISettings):
    amqp: SmtpAMQPConnectionSettings


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: SmtpFastRAMQPISettings

    mo_url: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://mo-service:5000"),
        description="Base URL for OS2mo.",
    )

    client_id: str = Field("bruce", description="Client ID for OIDC client.")
    client_secret: SecretStr = Field(..., description="Client Secret for OIDC client.")

    auth_server: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://keycloak-service:8080/auth"),
        description="Base URL for OIDC server (Keycloak).",
    )
    auth_realm: str = Field("mo", description="Realm to authenticate against")

    graphql_timeout: int = 120

    application_name: str = "os2mo_email_listener"

    active_agents: List[str] = Field(
        [], description="Agents which are actively listening and sending mails"
    )


class AgentSettings(BaseSettings):

    delay_on_error: int = Field(
        30,
        description="Amount of seconds to sleep before retrying AMQP messages",
    )


class EmailSettings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    sender: str = "os2mo@magenta.dk"
    smtp_port: int = Field(..., description="SMTP port")
    smtp_host: str = Field(..., description="SMTP host. For example 'smtp.gmail.com' ")
    testing: bool = Field(
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
