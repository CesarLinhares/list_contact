from typing import List, Optional, Dict
from pymongo import MongoClient

from project.src.core.entities import Contact
from project.src.core.enum.status import Status
from project.src.core import IList
from project.src.core.enum.phone_type import PhoneType
from project.src.repository import GetContactListContactsRepository


class CountContacts(IList):

    def __init__(self, infrastructure: MongoClient):
        self.infrastructure = infrastructure

    def get_list(self, optional_filter: Optional[dict] = {}) -> dict:
        contacts_repository = GetContactListContactsRepository(self.infrastructure)
        list_of_contacts: List[Contact] = contacts_repository.get(optional_filter)
        phones_types_count = self._count_phones_types(list_of_contacts)
        phones_types_result = [{
            "_id": phone_type,
            "Count": count
        } for phone_type, count in phones_types_count.items()]
        return {
            "countContacts": len(list_of_contacts),
            "countType": phones_types_result,
            "status": Status.SUCCESS.value,
        }

    @staticmethod
    def _count_phones_types(contact_list: List[Contact]) -> Dict[PhoneType, int]:
        phones_types_count = {
            phone_type: 0
            for phone_type in PhoneType.__members__
        }
        for contact in contact_list:
            for phone in contact.phoneList:
                phone_type = phone.type.value
                phones_types_count.update({
                    phone_type: phones_types_count.get(phone_type) + 1
                })
        return phones_types_count
