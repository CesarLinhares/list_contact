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
        contact_detail: Optional[Contact] = contact_detail_repository.get(_id)
        if not contact_detail:
            return {"status": Status.ERROR.value}
        contact_as_json = {
            "contactId": contact_detail.contactId,
            "firstName": contact_detail.name.firstName,
            "lastName": contact_detail.name.lastName,
            "email": contact_detail.email.email,
            "address": contact_detail.address.full_address,
            "phoneList": [{
                "number": phone.number,
                "type": phone.type,
            } for phone in contact_detail.phoneList],
            str(Status.SUCCESS.name).lower(): Status.SUCCESS.value,
        }
        return contact_as_json


class CountContacts(InterfaceList):

    def __init__(self, infrastructure: MongoClient):
        self.infrastructure = infrastructure

    def get_list(self, optional_filter: Optional[dict] = {}) -> dict:
        contacts_repository = GetContactList(self.infrastructure)
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


class ListsContacts(InterfaceList):

    def __init__(self, infrastructure: MongoClient):
        self.infrastructure = infrastructure

    def get_list(self, optional_filter: Optional[dict] = {}) -> dict:
        contacts_repository = GetContactList(self.infrastructure)
        list_of_contacts: List[Contact] = contacts_repository.get(optional_filter)
        list_of_contacts_return = [{
            "contactId": contact.contactId,
            "firstName": contact.name.firstName,
            "lastName": contact.name.lastName,
            "email": contact.email.email,
            "phoneList": [{
                "number": phone.number,
                "type": phone.type,
            } for phone in contact.phoneList]
        } for contact in list_of_contacts]
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
