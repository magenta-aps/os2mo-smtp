from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetEmailAddressType(BaseModel):
    facets: "TestingGetEmailAddressTypeFacets"


class TestingGetEmailAddressTypeFacets(BaseModel):
    objects: list["TestingGetEmailAddressTypeFacetsObjects"]


class TestingGetEmailAddressTypeFacetsObjects(BaseModel):
    current: Optional["TestingGetEmailAddressTypeFacetsObjectsCurrent"]


class TestingGetEmailAddressTypeFacetsObjectsCurrent(BaseModel):
    classes: list["TestingGetEmailAddressTypeFacetsObjectsCurrentClasses"]


class TestingGetEmailAddressTypeFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID


TestingGetEmailAddressType.update_forward_refs()
TestingGetEmailAddressTypeFacets.update_forward_refs()
TestingGetEmailAddressTypeFacetsObjects.update_forward_refs()
TestingGetEmailAddressTypeFacetsObjectsCurrent.update_forward_refs()
TestingGetEmailAddressTypeFacetsObjectsCurrentClasses.update_forward_refs()
