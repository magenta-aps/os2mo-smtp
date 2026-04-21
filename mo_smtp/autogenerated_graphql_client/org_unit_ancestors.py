from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class OrgUnitAncestors(BaseModel):
    org_units: "OrgUnitAncestorsOrgUnits"


class OrgUnitAncestorsOrgUnits(BaseModel):
    objects: list["OrgUnitAncestorsOrgUnitsObjects"]


class OrgUnitAncestorsOrgUnitsObjects(BaseModel):
    current: Optional["OrgUnitAncestorsOrgUnitsObjectsCurrent"]


class OrgUnitAncestorsOrgUnitsObjectsCurrent(BaseModel):
    uuid: UUID
    ancestors: list["OrgUnitAncestorsOrgUnitsObjectsCurrentAncestors"]
    name: str


class OrgUnitAncestorsOrgUnitsObjectsCurrentAncestors(BaseModel):
    uuid: UUID
    name: str


OrgUnitAncestors.update_forward_refs()
OrgUnitAncestorsOrgUnits.update_forward_refs()
OrgUnitAncestorsOrgUnitsObjects.update_forward_refs()
OrgUnitAncestorsOrgUnitsObjectsCurrent.update_forward_refs()
OrgUnitAncestorsOrgUnitsObjectsCurrentAncestors.update_forward_refs()
