from typing import List

from pydantic import BaseModel, validator

from src.core.enum.phone_type import PhoneType


class Phone(BaseModel):
    type: PhoneType
    number: str


def assert_have_max_of_3(phone_list: list):
    if len(phone_list) > 3:
        raise ValueError("Phone List must be less than 3")
    return phone_list


class PhoneList(BaseModel):
    phoneList: List[Phone]

    _max_3_phones = validator('phoneList', allow_reuse=True)(assert_have_max_of_3)
