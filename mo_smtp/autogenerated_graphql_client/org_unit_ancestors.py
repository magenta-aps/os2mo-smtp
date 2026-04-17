from typing import List, Optional

from .base_model import BaseModel


class OrgUnitAncestors(BaseModel):
    org_units: "OrgUnitAncestorsOrgUnits"


class OrgUnitAncestorsOrgUnits(BaseModel):
    objects: List["OrgUnitAncestorsOrgUnitsObjects"]


class OrgUnitAncestorsOrgUnitsObjects(BaseModel):
    current: Optional["OrgUnitAncestorsOrgUnitsObjectsCurrent"]


class OrgUnitAncestorsOrgUnitsObjectsCurrent(BaseModel):
    ancestors: List["OrgUnitAncestorsOrgUnitsObjectsCurrentAncestors"]
    name: str


class OrgUnitAncestorsOrgUnitsObjectsCurrentAncestors(BaseModel):
    name: str


OrgUnitAncestors.update_forward_refs()
OrgUnitAncestorsOrgUnits.update_forward_refs()
OrgUnitAncestorsOrgUnitsObjects.update_forward_refs()
OrgUnitAncestorsOrgUnitsObjectsCurrent.update_forward_refs()
OrgUnitAncestorsOrgUnitsObjectsCurrentAncestors.update_forward_refs()
