from hashlib import md5

from src.core.entities.address import Address
from src.core.entities.contacts import ContactParameters, Contact
from src.core.entities.email import Email
from src.core.entities.name import Name
from src.core.entities.phones import Phone
from src.core.enum.active import ActiveCondition


def _create_id(contact: dict) -> str:
    _id = (
        f"{contact.get('firstName') + contact.get('lastName')}:"
        f"{contact.get('email')}:"
        f"{contact.get('phoneList')[0].get('number')}"
    )
    return md5(_id.encode()).hexdigest()


def contact_modeling(contact_parameters: dict) -> dict:
    contact = contact_parameters
    contact.update({'_id': str(_create_id(contact)), 'active': True})
    return contact
