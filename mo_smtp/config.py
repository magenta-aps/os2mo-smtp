from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import AmqpDsn
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import SecretStr


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings"
    )

    amqp_url: AmqpDsn = parse_obj_as(AmqpDsn, "amqp://guest:guest@localhost:5672")
    amqp_exchange: str = "os2mo"

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


class RoutingKeys(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    employee_address_create: str = "employee.address.create"


class EmailSettings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    sender: str = "os2mo@magenta.dk"
    smtp_port: int = 25
    smtp_host: str = "smtp4dev"
    testing: bool = False
    texttype: str = "plain"
