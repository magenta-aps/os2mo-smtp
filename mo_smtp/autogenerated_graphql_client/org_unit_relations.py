from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class OrgUnitRelations(BaseModel):
    org_units: "OrgUnitRelationsOrgUnits"


class OrgUnitRelationsOrgUnits(BaseModel):
    objects: List["OrgUnitRelationsOrgUnitsObjects"]


class OrgUnitRelationsOrgUnitsObjects(BaseModel):
    current: Optional["OrgUnitRelationsOrgUnitsObjectsCurrent"]


class OrgUnitRelationsOrgUnitsObjectsCurrent(BaseModel):
    name: str
    root: Optional[List["OrgUnitRelationsOrgUnitsObjectsCurrentRoot"]]
    engagements: List["OrgUnitRelationsOrgUnitsObjectsCurrentEngagements"]
    related_units: List["OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnits"]


class OrgUnitRelationsOrgUnitsObjectsCurrentRoot(BaseModel):
    uuid: UUID


class OrgUnitRelationsOrgUnitsObjectsCurrentEngagements(BaseModel):
    uuid: UUID


class OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnits(BaseModel):
    org_units: List["OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnits"]


class OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnits(BaseModel):
    uuid: UUID
    root: Optional[
        List["OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnitsRoot"]
    ]


class OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnitsRoot(BaseModel):
    uuid: UUID


OrgUnitRelations.update_forward_refs()
OrgUnitRelationsOrgUnits.update_forward_refs()
OrgUnitRelationsOrgUnitsObjects.update_forward_refs()
OrgUnitRelationsOrgUnitsObjectsCurrent.update_forward_refs()
OrgUnitRelationsOrgUnitsObjectsCurrentRoot.update_forward_refs()
OrgUnitRelationsOrgUnitsObjectsCurrentEngagements.update_forward_refs()
OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnits.update_forward_refs()
OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnits.update_forward_refs()
OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnitsRoot.update_forward_refs()
