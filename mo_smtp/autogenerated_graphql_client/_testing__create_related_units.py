from uuid import UUID

from .base_model import BaseModel


class TestingCreateRelatedUnits(BaseModel):
    related_units_update: "TestingCreateRelatedUnitsRelatedUnitsUpdate"


class TestingCreateRelatedUnitsRelatedUnitsUpdate(BaseModel):
    uuid: UUID


TestingCreateRelatedUnits.update_forward_refs()
TestingCreateRelatedUnitsRelatedUnitsUpdate.update_forward_refs()
