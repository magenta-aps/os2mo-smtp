from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class OrgUnitRelations(BaseModel):
    org_units: "OrgUnitRelationsOrgUnits"


class OrgUnitRelationsOrgUnits(BaseModel):
    objects: list["OrgUnitRelationsOrgUnitsObjects"]


class OrgUnitRelationsOrgUnitsObjects(BaseModel):
    current: Optional["OrgUnitRelationsOrgUnitsObjectsCurrent"]


class OrgUnitRelationsOrgUnitsObjectsCurrent(BaseModel):
    name: str
    root: list["OrgUnitRelationsOrgUnitsObjectsCurrentRoot"] | None
    engagements: list["OrgUnitRelationsOrgUnitsObjectsCurrentEngagements"]
    related_units: list["OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnits"]


class OrgUnitRelationsOrgUnitsObjectsCurrentRoot(BaseModel):
    uuid: UUID


class OrgUnitRelationsOrgUnitsObjectsCurrentEngagements(BaseModel):
    uuid: UUID


class OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnits(BaseModel):
    org_units: list["OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnits"]


class OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnits(BaseModel):
    uuid: UUID
    root: (
        None | (list["OrgUnitRelationsOrgUnitsObjectsCurrentRelatedUnitsOrgUnitsRoot"])
    )


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
