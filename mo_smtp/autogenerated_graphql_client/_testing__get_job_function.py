from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetJobFunction(BaseModel):
    facets: "TestingGetJobFunctionFacets"


class TestingGetJobFunctionFacets(BaseModel):
    objects: list["TestingGetJobFunctionFacetsObjects"]


class TestingGetJobFunctionFacetsObjects(BaseModel):
    current: Optional["TestingGetJobFunctionFacetsObjectsCurrent"]


class TestingGetJobFunctionFacetsObjectsCurrent(BaseModel):
    classes: list["TestingGetJobFunctionFacetsObjectsCurrentClasses"]


class TestingGetJobFunctionFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID


TestingGetJobFunction.update_forward_refs()
TestingGetJobFunctionFacets.update_forward_refs()
TestingGetJobFunctionFacetsObjects.update_forward_refs()
TestingGetJobFunctionFacetsObjectsCurrent.update_forward_refs()
TestingGetJobFunctionFacetsObjectsCurrentClasses.update_forward_refs()
