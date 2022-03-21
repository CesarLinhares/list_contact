from typing import Optional, List, Dict, Callable, Any

from pydantic import BaseModel
from pymongo import MongoClient
from redis import Redis

from project.src.core.entities.active import Active
from project.src.core.entities.address import Address
from project.src.core.entities.contacts import Contact, ContactParameters, ContactOptionalParameters
from project.src.core.entities.email import Email
from project.src.core.entities.name import FirstName, LastName
from project.src.core.entities.phones import PhoneList, Phone
from project.src.core.enum.phone_type import PhoneType
from project.src.core.enum.status import Status
from project.src.core.interfaces.services_interfaces import InterfaceDetail, InterfaceList, InterfaceRegister, \
    InterfaceDelete, InterfaceUpdate
from project.src.repository.repository_actions import GetContact, GetContactList, SetExistentContact, SetNewContact, \
    SoftDeleteContact
from project.src.services.utilities.transform_parameters_to_contact import transform_parameters_to_contact


class ContactDetail(InterfaceDetail):
    def __init__(self, infrastructure: MongoClient):
        self.infrastructure = infrastructure

    def get_detail(self, _id: str) -> dict:
        contact_detail_repository = GetContact(self.infrastructure)
        contact_detail = contact_detail_repository.get(_id)
        contact_detail.pop("active")
        if not contact_detail:
            return {"status": Status.ERROR.value}
        return contact_detail


class CountContacts(InterfaceList):

    def __init__(self, infrastructure: MongoClient):
        self.infrastructure = infrastructure
        self.countContact = []
        self.phone_type = []

    def get_list(self, optional_filter: Optional[dict] = {}) -> dict:
        contacts_repository = GetContactList(self.infrastructure)
        list_of_contacts = contacts_repository.get(optional_filter)
        l1 = list_of_contacts
        l2 = list_of_contacts
        for nunContact in list_of_contacts:
            self.countContact.append(nunContact["_id"])
            for phones in nunContact['phones']:
                self.phone_type.append(phones.get('type'))


        return_json = {
            "countContacts": len(self.countContact),
            "countType": [
                {
                    "_id": "residential",
                    "Count": self.phone_type.count("residential")
                },
                {
                    "_id": "mobile",
                    "Count": self.phone_type.count("mobile"),
                },
                {
                    "_id": "commercial",
                    "Count": self.phone_type.count("commercial")
                }
            ]
        }
        return return_json


class ListsContacts(InterfaceList):

    def __init__(self, infrastructure: MongoClient):
        self.infrastructure = infrastructure

    def get_list(self, optional_filter: Optional[dict] = {}) -> dict:
        contacts_repository = GetContactList(self.infrastructure)
        list_of_contacts = contacts_repository.get(optional_filter)
        list_of_contacts_return = []
        for contact in list_of_contacts:
            contact.pop("active")
            list_of_contacts_return.append(contact)
        if not list_of_contacts_return:
            return {'status': Status.ERROR.value}
        return {'contactsList': list_of_contacts_return, 'status': Status.SUCCESS.value}


class RegisterContact(InterfaceRegister):
    status_alias = {
        True: Status.SUCCESS.value,
        False: Status.ERROR.value
    }

    def __init__(
            self,
            mongo_infrastructure: MongoClient,
            redis_infrastructure: Redis,
    ):
        self.mongo_infrastructure = mongo_infrastructure
        self.redis_repository = SoftDeleteContact(redis_infrastructure)
        self.register_methods_if_history = {
            True: lambda contact: all((
                self._clean_contact_history(contact),
                self._update_contact_in_mongo(contact)
            )),
            False: lambda contact: self._register_contact_in_mongo(contact),
        }

    def register(self, contact_parameters: ContactParameters) -> dict:
        contact = transform_parameters_to_contact(contact_parameters)
        has_deletion_history = self._check_contact_history(contact)
        register_method = self.register_methods_if_history.get(has_deletion_history)
        register_status = register_method(contact)
        return_status = self.status_alias.get(register_status)
        register_return = {"status": return_status}
        return register_return

    def _update_contact_in_mongo(self, contact: Contact) -> bool:
        repository = SetExistentContact(self.mongo_infrastructure)
        status_active = Active(is_active=True)
        return repository.update_contact(contact.contactId, {'status': status_active.is_active})

    def _check_contact_history(self, contact: dict) -> bool:
        return self.redis_repository.verify_if_contact_was_deleted(contact)

    def _clean_contact_history(self, contact: dict) -> bool:
        return self.redis_repository.delete_contact_from_redis(contact)

    def _register_contact_in_mongo(self, contact: dict) -> bool:
        contacts_repository = SetNewContact(self.mongo_infrastructure)
        return contacts_repository.register(contact)


class DeleteContact(InterfaceDelete):
    status_alias = {
        True: Status.SUCCESS.value,
        False: Status.ERROR.value
    }

    def __init__(
            self,
            mongo_infrastructure: MongoClient,
            redis_infrastructure: Redis,
    ):
        self.mongo_infrastructure = mongo_infrastructure
        self.redis_repository = SoftDeleteContact(redis_infrastructure)

    def delete(self, contact_id: str) -> dict:
        update_repository = SetExistentContact(self.mongo_infrastructure)
        get_repository = GetContact(self.mongo_infrastructure)
        contact = get_repository.get(contact_id)
        if not contact:
            return {'status': self.status_alias.get(False)}
        add_to_redis = self.redis_repository.add_contact_to_redis(contact)
        update_repository.update_contact(contact_id, {'active': False})
        return {'status': self.status_alias.get(update_repository and add_to_redis)}


class UpdateContact(InterfaceUpdate):
    status_alias = {
        True: Status.SUCCESS.value,
        False: Status.ERROR.value
    }
    update_wrapp_methods_per_field: Dict[str, Callable[[Any], BaseModel]] = {
        "firstName": lambda name: FirstName(firstName=name),
        "lastName": lambda name: LastName(lastName=name),
        "email": lambda email: Email(email=email),
        "address": lambda address: Address(full_address=address),
        "phoneList": lambda phone_list: PhoneList(phoneList=[
            Phone(type=phone.get("type"), number=phone.get("number"))
            for phone in phone_list]),
    }

    def __init__(self, mongo_infrastructure):
        self.mongo_infrastructure = mongo_infrastructure

    def update(self, contact_id: str, contact: ContactOptionalParameters) -> dict:
        updates_list = self._parameter_adjuster(contact)
        repository_update = SetExistentContact(self.mongo_infrastructure)
        update_status = repository_update.update_contact(contact_id, updates_list)
        return {"status": self.status_alias.get(update_status)}

    def _parameter_adjuster(self, contact: ContactOptionalParameters) -> dict:
        phone_numbers = []
        for number in contact.phoneList:
            phone = {'type': number.type.value, 'number': number.number}
            phone_numbers.append(phone)
        updates_dict = contact.dict()
        updates_dict.update({'phoneList': phone_numbers})
        return updates_dict

    def _wrapp_contact_parameters_in_update_entities(self, contact: ContactOptionalParameters) -> list:
        updates_dict = contact.dict()
        print(updates_dict)
        for key in filter(lambda x: updates_dict.get(x) is not None, updates_dict):
            update_wrapp_method = self.update_wrapp_methods_per_field.get(key)
            update_value = update_wrapp_method(updates_dict.get(key))
            yield update_value
