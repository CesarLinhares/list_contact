from typing import Dict, Callable, Any

from pydantic import BaseModel

from project.src.core.entities import Address
from project.src.core.entities import ContactOptionalParameters
from project.src.core.entities import Email
from project.src.core.entities import FirstName, LastName
from project.src.core.entities import PhoneList, Phone
from project.src.core.enum.status import Status
from project.src.core import IUpdate
from project.src.repository import UpdateContactRepository


class UpdateContact(IUpdate):
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
        updates_list = self._wrapp_contact_parameters_in_update_entities(contact)
        repository = UpdateContactRepository(self.mongo_infrastructure)
        update_status = repository.update_contact(contact_id, updates_list)
        return {"status": self.status_alias.get(update_status)}

    def _wrapp_contact_parameters_in_update_entities(self, contact: ContactOptionalParameters) -> list:
        updates_dict = contact.dict()
        for key in filter(lambda x: updates_dict.get(x) is not None, updates_dict):
            update_wrapp_method = self.update_wrapp_methods_per_field.get(key)
            update_value = update_wrapp_method(updates_dict.get(key))
            yield update_value
