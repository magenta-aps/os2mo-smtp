from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class Ituser(BaseModel):
    itusers: "ItuserItusers"


class ItuserItusers(BaseModel):
    objects: list["ItuserItusersObjects"]


class ItuserItusersObjects(BaseModel):
    current: Optional["ItuserItusersObjectsCurrent"]


class ItuserItusersObjectsCurrent(BaseModel):
    user_key: str
    rolebindings: list["ItuserItusersObjectsCurrentRolebindings"]
    person: list["ItuserItusersObjectsCurrentPerson"] | None
    itsystem: "ItuserItusersObjectsCurrentItsystem"


class ItuserItusersObjectsCurrentRolebindings(BaseModel):
    role: list["ItuserItusersObjectsCurrentRolebindingsRole"]


class ItuserItusersObjectsCurrentRolebindingsRole(BaseModel):
    name: str
    uuid: UUID


class ItuserItusersObjectsCurrentPerson(BaseModel):
    name: str
    uuid: UUID


class ItuserItusersObjectsCurrentItsystem(BaseModel):
    name: str
    uuid: UUID


Ituser.update_forward_refs()
ItuserItusers.update_forward_refs()
ItuserItusersObjects.update_forward_refs()
ItuserItusersObjectsCurrent.update_forward_refs()
ItuserItusersObjectsCurrentRolebindings.update_forward_refs()
ItuserItusersObjectsCurrentRolebindingsRole.update_forward_refs()
ItuserItusersObjectsCurrentPerson.update_forward_refs()
ItuserItusersObjectsCurrentItsystem.update_forward_refs()
