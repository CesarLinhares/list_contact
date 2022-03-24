from typing import List, Iterator, Optional

from src.core.entities.contacts import Contact
from src.core.enum.active import ActiveCondition
from src.repository.MongoActions import MongoActions
from src.repository.RedisActions import RedisActions
from src.repository.utilities.convert_dict_to_contact import convert_dict_to_contact


class GetContact(MongoActions):

    def get(self, identity: str):
        return self.find_one(identity, ActiveCondition.ACTIVE.value)


class GetContactList(MongoActions):
    def get(self, optional_filter: Optional[dict] = {}) -> List[dict]:
        list_of_contacts = self.find_all({**optional_filter, **ActiveCondition.ACTIVE.value})
        return list_of_contacts


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
