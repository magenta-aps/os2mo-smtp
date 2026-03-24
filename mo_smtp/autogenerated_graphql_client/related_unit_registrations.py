from typing import Annotated, Literal, Optional, Union
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class RelatedUnitRegistrations(BaseModel):
    registrations: "RelatedUnitRegistrationsRegistrations"


class RelatedUnitRegistrationsRegistrations(BaseModel):
    objects: list[
        Annotated[
            Union[
                "RelatedUnitRegistrationsRegistrationsObjectsIRegistration",
                "RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistration",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class RelatedUnitRegistrationsRegistrationsObjectsIRegistration(BaseModel):
    typename__: Literal[
        "AddressRegistration",
        "AssociationRegistration",
        "ClassRegistration",
        "EngagementRegistration",
        "FacetRegistration",
        "IRegistration",
        "ITSystemRegistration",
        "ITUserRegistration",
        "KLERegistration",
        "LeaveRegistration",
        "ManagerRegistration",
        "OrganisationUnitRegistration",
        "OwnerRegistration",
        "PersonRegistration",
        "RoleBindingRegistration",
    ] = Field(alias="__typename")


class RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistration(BaseModel):
    typename__: Literal["RelatedUnitRegistration"] = Field(alias="__typename")
    validities: list[
        "RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValidities"
    ]


class RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValidities(
    BaseModel
):
    org_units_response: "RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponse"


class RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponse(
    BaseModel
):
    objects: list[
        "RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjects"
    ]


class RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjects(
    BaseModel
):
    current: Optional[
        "RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjectsCurrent"
    ]


class RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjectsCurrent(
    BaseModel
):
    uuid: UUID
    root: (
        None
        | (
            list[
                "RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjectsCurrentRoot"
            ]
        )
    )


class RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjectsCurrentRoot(
    BaseModel
):
    uuid: UUID


RelatedUnitRegistrations.update_forward_refs()
RelatedUnitRegistrationsRegistrations.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsIRegistration.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistration.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValidities.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponse.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjects.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjectsCurrent.update_forward_refs()
RelatedUnitRegistrationsRegistrationsObjectsRelatedUnitRegistrationValiditiesOrgUnitsResponseObjectsCurrentRoot.update_forward_refs()
