from typing import Dict, Type, Callable, Union
from typing import List, Iterator, Optional

from pydantic import BaseModel

from project.src.core.entities.active import Active
from project.src.core.entities.address import Address
from project.src.core.entities.contacts import Contact
from project.src.core.entities.email import Email
from project.src.core.entities.name import LastName, FirstName
from project.src.core.entities.phones import PhoneList
from project.src.core.enum.active import ActiveCondition
from project.src.repository.MongoActions import MongoActions
from project.src.repository.RedisActions import RedisActions
from project.src.repository.utilities.convert_dict_to_contact import convert_dict_to_contact


class GetContact(MongoActions):

    def get(self, identity: str):
        return self.find_one(identity, ActiveCondition.ACTIVE.value)


class GetContactList(MongoActions):
    def get(self, optional_filter: Optional[dict] = {}) -> List[dict]:
        list_of_contacts = self.find_all({**optional_filter, **ActiveCondition.ACTIVE.value})
        return list_of_contacts


class SetNewContact(MongoActions):
    def register(self, contact: Contact) -> bool:
        contact_as_json = {
            "_id": contact.contactId,
            "firstName": contact.name.firstName,
            "lastName": contact.name.lastName,
            "email": contact.email.email,
            "address": contact.address.full_address,
            "phones": [{
                "type": phone.type.value,
                "number": phone.number,
            } for phone in contact.phoneList],
            **ActiveCondition.ACTIVE.value,
        }
        insert_status = self.insert_one(contact_as_json)
        return insert_status


class SoftDeleteContact(RedisActions):
    def verify_if_contact_was_deleted(self, contact: Contact) -> bool:
        contact_id = contact.contactId
        exists = self.verify_if_exists(contact_id)
        return exists

    def delete_contact_from_redis(self, contact: Contact) -> bool:
        contact_id = contact.contactId
        exclude = self.exclude(contact_id)
        return exclude

    def add_contact_to_redis(self, contact: Contact) -> bool:
        contact_id = contact.contactId
        add = self.insert(contact_id)
        return add


class SetExistentContact(MongoActions):
    updates_per_entity_methods: Dict[Type[BaseModel], Callable[[BaseModel], dict]] = {
        FirstName: lambda entity_name: {"firstName": entity_name.firstName},
        LastName: lambda entity_name: {"lastName": entity_name.lastName},
        Address: lambda entity_address: {"address": entity_address.full_address},
        Active: lambda entity_active: {"active": entity_active.is_active},
        Email: lambda entity_email: {"email": entity_email.email},
        PhoneList: lambda entity_phone_list: {"phones": [{
            "type": phone.type.value,
            "number": phone.number,
        } for phone in entity_phone_list.phoneList]},
    }

    def update_contact(self, contact_id: str, updates: List[Union[FirstName, LastName, Email, Address, Active, PhoneList]]) -> bool:
        updates_json = {}
        for unique_update in updates:
            update_method = self.updates_per_entity_methods.get(type(unique_update))
            unique_update_json: dict = update_method(unique_update)
            updates_json.update(unique_update_json)
        return self.update_one(contact_id, updates_json)