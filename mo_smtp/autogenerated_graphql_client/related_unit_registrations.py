from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class RelatedUnitRegistrations(BaseModel):
    related_units: "RelatedUnitRegistrationsRelatedUnits"


class RelatedUnitRegistrationsRelatedUnits(BaseModel):
    objects: list["RelatedUnitRegistrationsRelatedUnitsObjects"]


class RelatedUnitRegistrationsRelatedUnitsObjects(BaseModel):
    registrations: list["RelatedUnitRegistrationsRelatedUnitsObjectsRegistrations"]


class RelatedUnitRegistrationsRelatedUnitsObjectsRegistrations(BaseModel):
    validities: list[
        "RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValidities"
    ]


class RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValidities(BaseModel):
    org_units_response: "RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponse"


class RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponse(
    BaseModel
):
    objects: list[
        "RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjects"
    ]


class RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjects(
    BaseModel
):
    uuid: UUID
    current: Optional[
        "RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjectsCurrent"
    ]


class RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjectsCurrent(
    BaseModel
):
    root: (
        None
        | (
            list[
                "RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjectsCurrentRoot"
            ]
        )
    )


class RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjectsCurrentRoot(
    BaseModel
):
    uuid: UUID


RelatedUnitRegistrations.update_forward_refs()
RelatedUnitRegistrationsRelatedUnits.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjects.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjectsRegistrations.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValidities.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponse.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjects.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjectsCurrent.update_forward_refs()
RelatedUnitRegistrationsRelatedUnitsObjectsRegistrationsValiditiesOrgUnitsResponseObjectsCurrentRoot.update_forward_refs()
