from uuid import UUID

from .base_model import BaseModel


class TestingCreateRolebinding(BaseModel):
    rolebinding_create: "TestingCreateRolebindingRolebindingCreate"


class TestingCreateRolebindingRolebindingCreate(BaseModel):
    uuid: UUID


TestingCreateRolebinding.update_forward_refs()
TestingCreateRolebindingRolebindingCreate.update_forward_refs()
