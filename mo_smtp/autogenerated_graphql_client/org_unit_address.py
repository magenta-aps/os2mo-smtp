from typing import Optional

from .base_model import BaseModel


class OrgUnitAddress(BaseModel):
    org_units: "OrgUnitAddressOrgUnits"


class OrgUnitAddressOrgUnits(BaseModel):
    objects: list["OrgUnitAddressOrgUnitsObjects"]


class OrgUnitAddressOrgUnitsObjects(BaseModel):
    current: Optional["OrgUnitAddressOrgUnitsObjectsCurrent"]


class OrgUnitAddressOrgUnitsObjectsCurrent(BaseModel):
    addresses: list["OrgUnitAddressOrgUnitsObjectsCurrentAddresses"]


class OrgUnitAddressOrgUnitsObjectsCurrentAddresses(BaseModel):
    value: str


OrgUnitAddress.update_forward_refs()
OrgUnitAddressOrgUnits.update_forward_refs()
OrgUnitAddressOrgUnitsObjects.update_forward_refs()
OrgUnitAddressOrgUnitsObjectsCurrent.update_forward_refs()
OrgUnitAddressOrgUnitsObjectsCurrentAddresses.update_forward_refs()
