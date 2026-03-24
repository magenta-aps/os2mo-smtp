from uuid import UUID

from .base_model import BaseModel


class RelatedUnits(BaseModel):
    related_units: "RelatedUnitsRelatedUnits"


class RelatedUnitsRelatedUnits(BaseModel):
    objects: list["RelatedUnitsRelatedUnitsObjects"]


class RelatedUnitsRelatedUnitsObjects(BaseModel):
    validities: list["RelatedUnitsRelatedUnitsObjectsValidities"]


class RelatedUnitsRelatedUnitsObjectsValidities(BaseModel):
    org_units: list["RelatedUnitsRelatedUnitsObjectsValiditiesOrgUnits"]


class RelatedUnitsRelatedUnitsObjectsValiditiesOrgUnits(BaseModel):
    uuid: UUID
    root: list["RelatedUnitsRelatedUnitsObjectsValiditiesOrgUnitsRoot"] | None


class RelatedUnitsRelatedUnitsObjectsValiditiesOrgUnitsRoot(BaseModel):
    uuid: UUID


RelatedUnits.update_forward_refs()
RelatedUnitsRelatedUnits.update_forward_refs()
RelatedUnitsRelatedUnitsObjects.update_forward_refs()
RelatedUnitsRelatedUnitsObjectsValidities.update_forward_refs()
RelatedUnitsRelatedUnitsObjectsValiditiesOrgUnits.update_forward_refs()
RelatedUnitsRelatedUnitsObjectsValiditiesOrgUnitsRoot.update_forward_refs()
