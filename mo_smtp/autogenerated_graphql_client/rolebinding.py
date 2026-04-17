from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class Rolebinding(BaseModel):
    rolebindings: "RolebindingRolebindings"


class RolebindingRolebindings(BaseModel):
    objects: List["RolebindingRolebindingsObjects"]


class RolebindingRolebindingsObjects(BaseModel):
    current: Optional["RolebindingRolebindingsObjectsCurrent"]


class RolebindingRolebindingsObjectsCurrent(BaseModel):
    ituser: List["RolebindingRolebindingsObjectsCurrentItuser"]


class RolebindingRolebindingsObjectsCurrentItuser(BaseModel):
    uuid: UUID


Rolebinding.update_forward_refs()
RolebindingRolebindings.update_forward_refs()
RolebindingRolebindingsObjects.update_forward_refs()
RolebindingRolebindingsObjectsCurrent.update_forward_refs()
RolebindingRolebindingsObjectsCurrentItuser.update_forward_refs()
