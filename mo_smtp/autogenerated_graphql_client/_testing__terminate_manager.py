from uuid import UUID

from .base_model import BaseModel


class TestingTerminateManager(BaseModel):
    manager_terminate: "TestingTerminateManagerManagerTerminate"


class TestingTerminateManagerManagerTerminate(BaseModel):
    uuid: UUID


TestingTerminateManager.update_forward_refs()
TestingTerminateManagerManagerTerminate.update_forward_refs()
