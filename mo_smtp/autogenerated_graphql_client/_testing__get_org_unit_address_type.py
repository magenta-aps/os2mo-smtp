from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetOrgUnitAddressType(BaseModel):
    facets: "TestingGetOrgUnitAddressTypeFacets"


class TestingGetOrgUnitAddressTypeFacets(BaseModel):
    objects: List["TestingGetOrgUnitAddressTypeFacetsObjects"]


class TestingGetOrgUnitAddressTypeFacetsObjects(BaseModel):
    current: Optional["TestingGetOrgUnitAddressTypeFacetsObjectsCurrent"]


class TestingGetOrgUnitAddressTypeFacetsObjectsCurrent(BaseModel):
    classes: List["TestingGetOrgUnitAddressTypeFacetsObjectsCurrentClasses"]


class TestingGetOrgUnitAddressTypeFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID


TestingGetOrgUnitAddressType.update_forward_refs()
TestingGetOrgUnitAddressTypeFacets.update_forward_refs()
TestingGetOrgUnitAddressTypeFacetsObjects.update_forward_refs()
TestingGetOrgUnitAddressTypeFacetsObjectsCurrent.update_forward_refs()
TestingGetOrgUnitAddressTypeFacetsObjectsCurrentClasses.update_forward_refs()
