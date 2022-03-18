from typing import Dict, Callable

from pymongo import MongoClient
from redis import Redis

from project.src.core.entities import Active
from project.src.core.enum.status import Status
from project.src.core.entities import Contact, ContactParameters
from project.src.core import IRegister
from project.src.repository import RegisterContactsRepository
from project.src.repository import SoftDeleteRegisters
from project.src.repository import UpdateContactRepository
from project.src.services.utils.transform_parameters_to_contact import transform_parameters_to_contact


class RegisterContact(IRegister):
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
        self.redis_repository = SoftDeleteRegisters(redis_infrastructure)
        self.register_methods_if_history: Dict[bool, Callable[[Contact], bool]] = {
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
        repository = UpdateContactRepository(self.mongo_infrastructure)
        status_active = Active(is_active=True)
        return repository.update_contact(contact.contactId, (status_active,))

    def _check_contact_history(self, contact: Contact) -> bool:
        return self.redis_repository.verify_if_contact_was_deleted(contact)

    def _clean_contact_history(self, contact: Contact) -> bool:
        return self.redis_repository.delete_contact_from_redis(contact)

    def _register_contact_in_mongo(self, contact: Contact) -> bool:
        contacts_repository = RegisterContactsRepository(self.mongo_infrastructure)
        return contacts_repository.register(contact)


