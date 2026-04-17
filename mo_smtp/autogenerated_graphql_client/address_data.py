from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class AddressData(BaseModel):
    addresses: "AddressDataAddresses"


class AddressDataAddresses(BaseModel):
    objects: List["AddressDataAddressesObjects"]


class AddressDataAddressesObjects(BaseModel):
    current: Optional["AddressDataAddressesObjectsCurrent"]


class AddressDataAddressesObjectsCurrent(BaseModel):
    value: str
    employee_uuid: Optional[UUID]
    address_type: "AddressDataAddressesObjectsCurrentAddressType"


class AddressDataAddressesObjectsCurrentAddressType(BaseModel):
    scope: Optional[str]


AddressData.update_forward_refs()
AddressDataAddresses.update_forward_refs()
AddressDataAddressesObjects.update_forward_refs()
AddressDataAddressesObjectsCurrent.update_forward_refs()
AddressDataAddressesObjectsCurrentAddressType.update_forward_refs()
