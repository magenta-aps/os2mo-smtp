from uuid import UUID

from .base_model import BaseModel


class TestingTerminateOrgUnit(BaseModel):
    org_unit_terminate: "TestingTerminateOrgUnitOrgUnitTerminate"


class TestingTerminateOrgUnitOrgUnitTerminate(BaseModel):
    uuid: UUID


TestingTerminateOrgUnit.update_forward_refs()
TestingTerminateOrgUnitOrgUnitTerminate.update_forward_refs()
