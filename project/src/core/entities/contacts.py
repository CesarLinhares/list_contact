from typing import List, Optional

from pydantic import BaseModel, validator

from src.core.entities.address import Address
from src.core.entities.email import Email
from src.core.entities.name import Name
from src.core.entities.phones import PhoneList, Phone, assert_have_max_of_3


class ContactParameters(BaseModel):
    email: str
    address: str
    lastName: str
    firstName: str
    phoneList: List[Phone]

    _max_3_phones = validator('phoneList', allow_reuse=True)(assert_have_max_of_3)


class ContactOptionalParameters(BaseModel):
    email: Optional[str] = None
    address: Optional[str] = None
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    phoneList: Optional[List[Phone]] = None

    _max_3_phones = validator('phoneList', allow_reuse=True)(assert_have_max_of_3)


class Contact(PhoneList):
    contactId: str
    name: Name
    email: Email
    address: Address

