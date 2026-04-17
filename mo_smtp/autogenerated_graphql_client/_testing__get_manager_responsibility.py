from uuid import UUID

from .base_model import BaseModel


class TestingGetManagerResponsibility(BaseModel):
    classes: "TestingGetManagerResponsibilityClasses"


class TestingGetManagerResponsibilityClasses(BaseModel):
    objects: list["TestingGetManagerResponsibilityClassesObjects"]


class TestingGetManagerResponsibilityClassesObjects(BaseModel):
    uuid: UUID


TestingGetManagerResponsibility.update_forward_refs()
TestingGetManagerResponsibilityClasses.update_forward_refs()
TestingGetManagerResponsibilityClassesObjects.update_forward_refs()
