from typing import List, Optional

from .base_model import BaseModel


class EmployeeData(BaseModel):
    employees: "EmployeeDataEmployees"


class EmployeeDataEmployees(BaseModel):
    objects: List["EmployeeDataEmployeesObjects"]


class EmployeeDataEmployeesObjects(BaseModel):
    current: Optional["EmployeeDataEmployeesObjectsCurrent"]


class EmployeeDataEmployeesObjectsCurrent(BaseModel):
    name: str
    addresses: List["EmployeeDataEmployeesObjectsCurrentAddresses"]
    engagements: List["EmployeeDataEmployeesObjectsCurrentEngagements"]


class EmployeeDataEmployeesObjectsCurrentAddresses(BaseModel):
    value: str


class EmployeeDataEmployeesObjectsCurrentEngagements(BaseModel):
    org_unit: List["EmployeeDataEmployeesObjectsCurrentEngagementsOrgUnit"]
    managers: List["EmployeeDataEmployeesObjectsCurrentEngagementsManagers"]


class EmployeeDataEmployeesObjectsCurrentEngagementsOrgUnit(BaseModel):
    name: str


class EmployeeDataEmployeesObjectsCurrentEngagementsManagers(BaseModel):
    person: Optional[
        List["EmployeeDataEmployeesObjectsCurrentEngagementsManagersPerson"]
    ]


class EmployeeDataEmployeesObjectsCurrentEngagementsManagersPerson(BaseModel):
    addresses: List[
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
