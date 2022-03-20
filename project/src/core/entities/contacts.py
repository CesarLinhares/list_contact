from pydantic import BaseModel


class Contact(PhoneList):
    contactId: str
    name: Name
    email: Email
    address: Address