# Generated by ariadne-codegen on 2023-08-17 13:58
# Source: queries.graphql

from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetOrgUnitData(BaseModel):
    org_units: "GetOrgUnitDataOrgUnits"


class GetOrgUnitDataOrgUnits(BaseModel):
    objects: List["GetOrgUnitDataOrgUnitsObjects"]


class GetOrgUnitDataOrgUnitsObjects(BaseModel):
    objects: List["GetOrgUnitDataOrgUnitsObjectsObjects"]


class GetOrgUnitDataOrgUnitsObjectsObjects(BaseModel):
    name: str
    user_key: str
    parent_uuid: Optional[UUID]
    managers: List["GetOrgUnitDataOrgUnitsObjectsObjectsManagers"]


class GetOrgUnitDataOrgUnitsObjectsObjectsManagers(BaseModel):
    employee_uuid: Optional[UUID]


GetOrgUnitData.update_forward_refs()
GetOrgUnitDataOrgUnits.update_forward_refs()
GetOrgUnitDataOrgUnitsObjects.update_forward_refs()
GetOrgUnitDataOrgUnitsObjectsObjects.update_forward_refs()
GetOrgUnitDataOrgUnitsObjectsObjectsManagers.update_forward_refs()
