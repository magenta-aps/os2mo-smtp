from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class Rolebinding(BaseModel):
    rolebindings: "RolebindingRolebindings"


class RolebindingRolebindings(BaseModel):
    objects: list["RolebindingRolebindingsObjects"]


class RolebindingRolebindingsObjects(BaseModel):
    current: Optional["RolebindingRolebindingsObjectsCurrent"]


class RolebindingRolebindingsObjectsCurrent(BaseModel):
    ituser: list["RolebindingRolebindingsObjectsCurrentItuser"]


class RolebindingRolebindingsObjectsCurrentItuser(BaseModel):
    uuid: UUID


Rolebinding.update_forward_refs()
RolebindingRolebindings.update_forward_refs()
RolebindingRolebindingsObjects.update_forward_refs()
RolebindingRolebindingsObjectsCurrent.update_forward_refs()
RolebindingRolebindingsObjectsCurrentItuser.update_forward_refs()
