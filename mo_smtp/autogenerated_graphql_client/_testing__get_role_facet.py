from uuid import UUID

from .base_model import BaseModel


class TestingGetRoleFacet(BaseModel):
    facets: "TestingGetRoleFacetFacets"


class TestingGetRoleFacetFacets(BaseModel):
    objects: list["TestingGetRoleFacetFacetsObjects"]


class TestingGetRoleFacetFacetsObjects(BaseModel):
    uuid: UUID


TestingGetRoleFacet.update_forward_refs()
TestingGetRoleFacetFacets.update_forward_refs()
TestingGetRoleFacetFacetsObjects.update_forward_refs()
