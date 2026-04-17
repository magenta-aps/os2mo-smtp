from uuid import UUID

from .base_model import BaseModel


class TestingGetRelatedUnitsForOrgUnit(BaseModel):
    related_units: "TestingGetRelatedUnitsForOrgUnitRelatedUnits"


class TestingGetRelatedUnitsForOrgUnitRelatedUnits(BaseModel):
    objects: list["TestingGetRelatedUnitsForOrgUnitRelatedUnitsObjects"]


class TestingGetRelatedUnitsForOrgUnitRelatedUnitsObjects(BaseModel):
    uuid: UUID


TestingGetRelatedUnitsForOrgUnit.update_forward_refs()
TestingGetRelatedUnitsForOrgUnitRelatedUnits.update_forward_refs()
TestingGetRelatedUnitsForOrgUnitRelatedUnitsObjects.update_forward_refs()
