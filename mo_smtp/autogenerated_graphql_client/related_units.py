from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class RelatedUnits(BaseModel):
    related_units: "RelatedUnitsRelatedUnits"


class RelatedUnitsRelatedUnits(BaseModel):
    objects: list["RelatedUnitsRelatedUnitsObjects"]


class RelatedUnitsRelatedUnitsObjects(BaseModel):
    current: Optional["RelatedUnitsRelatedUnitsObjectsCurrent"]


class RelatedUnitsRelatedUnitsObjectsCurrent(BaseModel):
    org_units: list["RelatedUnitsRelatedUnitsObjectsCurrentOrgUnits"]


class RelatedUnitsRelatedUnitsObjectsCurrentOrgUnits(BaseModel):
    uuid: UUID
    root: list["RelatedUnitsRelatedUnitsObjectsCurrentOrgUnitsRoot"] | None


class RelatedUnitsRelatedUnitsObjectsCurrentOrgUnitsRoot(BaseModel):
    uuid: UUID


RelatedUnits.update_forward_refs()
RelatedUnitsRelatedUnits.update_forward_refs()
RelatedUnitsRelatedUnitsObjects.update_forward_refs()
RelatedUnitsRelatedUnitsObjectsCurrent.update_forward_refs()
RelatedUnitsRelatedUnitsObjectsCurrentOrgUnits.update_forward_refs()
RelatedUnitsRelatedUnitsObjectsCurrentOrgUnitsRoot.update_forward_refs()
