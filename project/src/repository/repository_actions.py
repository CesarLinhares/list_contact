from typing import List, Iterator, Optional

from project.src.core.entities.contacts import Contact
from project.src.core.enum.active import ActiveCondition
from project.src.repository.MongoActions import MongoActions
from project.src.repository.RedisActions import RedisActions
from project.src.repository.utilities.convert_dict_to_contact import convert_dict_to_contact


class GetContact(MongoActions):

    def get(self, identity: str) -> dict:
        contact_detail_as_json = self.find_one(identity, ActiveCondition.ACTIVE.value)
        if not contact_detail_as_json:
            return
        contact_detail = convert_dict_to_contact(contact_detail_as_json)
        return contact_detail


class GetContactList(MongoActions):
    def get(self, optional_filter: Optional[dict] = {}) -> List[Contact]:
        list_of_contacts: Iterator[dict] = self.find_all({**optional_filter, **ActiveCondition.ACTIVE.value})
        list_of_contacts_return = [
            convert_dict_to_contact(contact_as_dict)
            for contact_as_dict in list_of_contacts
        ]
        return list_of_contacts_return


class SetNewContact(MongoActions):
    def register(self, contact: dict) -> bool:
        insert_status = self.insert_one(contact)
        return insert_status


class SoftDeleteContact(RedisActions):
    def verify_if_contact_was_deleted(self, contact: dict) -> bool:
        contact_id = contact.get('_id')
        exists = self.verify_if_exists(contact_id)
        return exists

    def delete_contact_from_redis(self, contact: dict) -> bool:
        contact_id = contact.get('_id')
        exclude = self.exclude(contact_id)
        return exclude

    def add_contact_to_redis(self, contact: dict) -> bool:
        contact_id = contact.get('_id')
        add = self.insert(contact_id)
        return add


class SetExistentContact(MongoActions):
    def update_contact(self, contact_id: str, updates: dict) -> bool:
        return self.update_one(contact_id, updates)
