from typing import List, Optional

from .base_model import BaseModel


class OrgUnitAddress(BaseModel):
    org_units: "OrgUnitAddressOrgUnits"


class OrgUnitAddressOrgUnits(BaseModel):
    objects: List["OrgUnitAddressOrgUnitsObjects"]


class OrgUnitAddressOrgUnitsObjects(BaseModel):
    current: Optional["OrgUnitAddressOrgUnitsObjectsCurrent"]


class OrgUnitAddressOrgUnitsObjectsCurrent(BaseModel):
    addresses: List["OrgUnitAddressOrgUnitsObjectsCurrentAddresses"]


class OrgUnitAddressOrgUnitsObjectsCurrentAddresses(BaseModel):
    value: str


OrgUnitAddress.update_forward_refs()
OrgUnitAddressOrgUnits.update_forward_refs()
OrgUnitAddressOrgUnitsObjects.update_forward_refs()
OrgUnitAddressOrgUnitsObjectsCurrent.update_forward_refs()
OrgUnitAddressOrgUnitsObjectsCurrentAddresses.update_forward_refs()
