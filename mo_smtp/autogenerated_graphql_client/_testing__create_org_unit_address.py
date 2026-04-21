from uuid import UUID

from .base_model import BaseModel


class TestingCreateOrgUnitAddress(BaseModel):
    address_create: "TestingCreateOrgUnitAddressAddressCreate"


class TestingCreateOrgUnitAddressAddressCreate(BaseModel):
    uuid: UUID


TestingCreateOrgUnitAddress.update_forward_refs()
TestingCreateOrgUnitAddressAddressCreate.update_forward_refs()
