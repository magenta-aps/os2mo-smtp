from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetRoleType(BaseModel):
    facets: "TestingGetRoleTypeFacets"


class TestingGetRoleTypeFacets(BaseModel):
    objects: List["TestingGetRoleTypeFacetsObjects"]


class TestingGetRoleTypeFacetsObjects(BaseModel):
    current: Optional["TestingGetRoleTypeFacetsObjectsCurrent"]


class TestingGetRoleTypeFacetsObjectsCurrent(BaseModel):
    classes: List["TestingGetRoleTypeFacetsObjectsCurrentClasses"]


class TestingGetRoleTypeFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID
    name: str


TestingGetRoleType.update_forward_refs()
TestingGetRoleTypeFacets.update_forward_refs()
TestingGetRoleTypeFacetsObjects.update_forward_refs()
TestingGetRoleTypeFacetsObjectsCurrent.update_forward_refs()
TestingGetRoleTypeFacetsObjectsCurrentClasses.update_forward_refs()
