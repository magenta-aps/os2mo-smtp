from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class GetManager(BaseModel):
    managers: "GetManagerManagers"


class GetManagerManagers(BaseModel):
    objects: list["GetManagerManagersObjects"]


class GetManagerManagersObjects(BaseModel):
    validities: list["GetManagerManagersObjectsValidities"]


class GetManagerManagersObjectsValidities(BaseModel):
    uuid: UUID
    person: list["GetManagerManagersObjectsValiditiesPerson"] | None
    org_unit: list["GetManagerManagersObjectsValiditiesOrgUnit"]
    validity: "GetManagerManagersObjectsValiditiesValidity"


class GetManagerManagersObjectsValiditiesPerson(BaseModel):
    name: str
    uuid: UUID


class GetManagerManagersObjectsValiditiesOrgUnit(BaseModel):
    name: str
    uuid: UUID


class GetManagerManagersObjectsValiditiesValidity(BaseModel):
    to: datetime | None
    from_: datetime = Field(alias="from")


GetManager.update_forward_refs()
GetManagerManagers.update_forward_refs()
GetManagerManagersObjects.update_forward_refs()
GetManagerManagersObjectsValidities.update_forward_refs()
GetManagerManagersObjectsValiditiesPerson.update_forward_refs()
GetManagerManagersObjectsValiditiesOrgUnit.update_forward_refs()
GetManagerManagersObjectsValiditiesValidity.update_forward_refs()
