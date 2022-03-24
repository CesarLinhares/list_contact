from src.core.entities.address import Address
from src.core.entities.contacts import Contact
from src.core.entities.email import Email
from src.core.entities.name import Name
from src.core.entities.phones import Phone


def convert_dict_to_contact(contact_as_dict: dict) -> Contact:
    contact = Contact(
        contactId=contact_as_dict.get("_id"),
        name=Name(
            firstName=contact_as_dict.get("firstName"),
            lastName=contact_as_dict.get("lastName"),
        ),
        email=Email(
            email=contact_as_dict.get('email')
        ),
        phoneList=[Phone(
            type=phone.get('type'),
            number=phone.get('number')
        ) for phone in contact_as_dict.get('phones')],
        address=Address(
            full_address=contact_as_dict.get('address')
        )
    )
    return contact

