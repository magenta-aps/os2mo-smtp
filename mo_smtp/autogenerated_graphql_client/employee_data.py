from typing import Optional

from .base_model import BaseModel


class EmployeeData(BaseModel):
    employees: "EmployeeDataEmployees"


class EmployeeDataEmployees(BaseModel):
    objects: list["EmployeeDataEmployeesObjects"]


class EmployeeDataEmployeesObjects(BaseModel):
    current: Optional["EmployeeDataEmployeesObjectsCurrent"]


class EmployeeDataEmployeesObjectsCurrent(BaseModel):
    name: str
    addresses: list["EmployeeDataEmployeesObjectsCurrentAddresses"]
    engagements: list["EmployeeDataEmployeesObjectsCurrentEngagements"]


class EmployeeDataEmployeesObjectsCurrentAddresses(BaseModel):
    value: str


class EmployeeDataEmployeesObjectsCurrentEngagements(BaseModel):
    org_unit: list["EmployeeDataEmployeesObjectsCurrentEngagementsOrgUnit"]
    managers: list["EmployeeDataEmployeesObjectsCurrentEngagementsManagers"]


class EmployeeDataEmployeesObjectsCurrentEngagementsOrgUnit(BaseModel):
    name: str


class EmployeeDataEmployeesObjectsCurrentEngagementsManagers(BaseModel):
    person: (
        None | (list["EmployeeDataEmployeesObjectsCurrentEngagementsManagersPerson"])
    )


class EmployeeDataEmployeesObjectsCurrentEngagementsManagersPerson(BaseModel):
    addresses: list[
        "EmployeeDataEmployeesObjectsCurrentEngagementsManagersPersonAddresses"
    ]


class EmployeeDataEmployeesObjectsCurrentEngagementsManagersPersonAddresses(BaseModel):
    value: str


EmployeeData.update_forward_refs()
EmployeeDataEmployees.update_forward_refs()
EmployeeDataEmployeesObjects.update_forward_refs()
EmployeeDataEmployeesObjectsCurrent.update_forward_refs()
EmployeeDataEmployeesObjectsCurrentAddresses.update_forward_refs()
EmployeeDataEmployeesObjectsCurrentEngagements.update_forward_refs()
EmployeeDataEmployeesObjectsCurrentEngagementsOrgUnit.update_forward_refs()
EmployeeDataEmployeesObjectsCurrentEngagementsManagers.update_forward_refs()
EmployeeDataEmployeesObjectsCurrentEngagementsManagersPerson.update_forward_refs()
EmployeeDataEmployeesObjectsCurrentEngagementsManagersPersonAddresses.update_forward_refs()
