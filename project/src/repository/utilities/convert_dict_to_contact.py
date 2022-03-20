from project.src.core.entities.address import Address
from project.src.core.entities.contacts import Contact
from project.src.core.entities.email import Email
from project.src.core.entities.name import Name
from project.src.core.entities.phones import Phone


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

