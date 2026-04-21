from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetPhoneAddressType(BaseModel):
    facets: "TestingGetPhoneAddressTypeFacets"


class TestingGetPhoneAddressTypeFacets(BaseModel):
    objects: list["TestingGetPhoneAddressTypeFacetsObjects"]


class TestingGetPhoneAddressTypeFacetsObjects(BaseModel):
    current: Optional["TestingGetPhoneAddressTypeFacetsObjectsCurrent"]


class TestingGetPhoneAddressTypeFacetsObjectsCurrent(BaseModel):
    classes: list["TestingGetPhoneAddressTypeFacetsObjectsCurrentClasses"]


class TestingGetPhoneAddressTypeFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID


TestingGetPhoneAddressType.update_forward_refs()
TestingGetPhoneAddressTypeFacets.update_forward_refs()
TestingGetPhoneAddressTypeFacetsObjects.update_forward_refs()
TestingGetPhoneAddressTypeFacetsObjectsCurrent.update_forward_refs()
TestingGetPhoneAddressTypeFacetsObjectsCurrentClasses.update_forward_refs()
