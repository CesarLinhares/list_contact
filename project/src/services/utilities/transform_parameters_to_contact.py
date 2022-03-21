from hashlib import md5

from project.src.core.entities.address import Address
from project.src.core.entities.contacts import ContactParameters, Contact
from project.src.core.entities.email import Email
from project.src.core.entities.name import Name
from project.src.core.entities.phones import Phone
from project.src.core.enum.active import ActiveCondition


def _create_id(contact: ContactParameters) -> str:
    _id = (
        f"{contact.firstName + contact.lastName}:"
        f"{contact.email}:"
        f"{contact.phoneList[0].number}"
    )
    return md5(_id.encode()).hexdigest()


def transform_parameters_to_contact(contact_parameters: ContactParameters) -> dict:
    contact = {
            "_id": _create_id(contact_parameters),
            "firstName": contact_parameters.firstName,
            "lastName": contact_parameters.lastName,
            "email": contact_parameters.email,
            "address": contact_parameters.address,
            "phones": [{
                "type": phone.type.value,
                "number": phone.number,
            } for phone in contact_parameters.phoneList],
            **ActiveCondition.ACTIVE.value,
        }

    return contact
