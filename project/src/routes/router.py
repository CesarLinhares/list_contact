from fastapi import APIRouter

from src.core.entities.contacts import ContactParameters, ContactOptionalParameters
from src.core.interfaces.services_interfaces import InterfaceRegister, InterfaceList, InterfaceDetail, \
    InterfaceUpdate, InterfaceDelete
from src.infrastructure.mongo_connection import MongoConnection
from src.infrastructure.redis_connection import RedisConnection
from src.services.service_actions import RegisterContact, ListsContacts, CountContacts, ContactDetail, \
    UpdateContact, DeleteContact
from src.services.utilities.env_config import config

route = APIRouter(prefix=config("ROUTERS_PREFIX"))


@route.post("/register")
def register_contact(contact: ContactParameters):
    mongo_connection = MongoConnection.get_singleton_connection()
    redis_connection = RedisConnection.get_singleton_connection()
    register_service: InterfaceRegister = RegisterContact(mongo_connection, redis_connection)
    register_return = register_service.register(contact.dict())
    return register_return


@route.get("/contacts")
def lists_contacts():
    mongo_connection = MongoConnection.get_singleton_connection()
    list_contact_service: InterfaceList = ListsContacts(mongo_connection)
    contacts_list = list_contact_service.get_list()
    return contacts_list


@route.get("/count")
def lists_phones():
    mongo_connection = MongoConnection.get_singleton_connection()
    count_contact_service: InterfaceList = CountContacts(mongo_connection)
    contacts_list = count_contact_service.get_list()
    return contacts_list


@route.get("/contact/{_id}")
def contact_detail(_id: str):
    mongo_connection = MongoConnection.get_singleton_connection()
    get_contact_detail_service: InterfaceDetail = ContactDetail(mongo_connection)
    contact_details = get_contact_detail_service.get_detail(_id)
    return contact_details


@route.put("/edit/{_id}")
def contact_update(_id: str, updates: ContactOptionalParameters):
    mongo_connection = MongoConnection.get_singleton_connection()
    get_contact_update_service: InterfaceUpdate = UpdateContact(mongo_connection)
    contact_updates = get_contact_update_service.update(_id, updates.dict())
    return contact_updates


@route.delete("/remove/{_id}")
def delete_contact(_id: str):
    mongo_connection = MongoConnection.get_singleton_connection()
    redis_connection = RedisConnection.get_singleton_connection()
    get_contact_delete_service: InterfaceDelete = DeleteContact(mongo_connection, redis_connection)
    contact_deleted = get_contact_delete_service.delete(_id)
    return contact_deleted


@route.get("/contacts/{letter}")
def list_contact_by_letter(letter: str):
    mongo_connection = MongoConnection.get_singleton_connection()
    list_contact_service: InterfaceList = ListsContacts(mongo_connection)
    filter_for_letter = {"firstName": {"$regex": f"^{letter.upper()}|^{letter.lower()}"}}
    contacts_list_for_letter = list_contact_service.get_list(filter_for_letter)
    return contacts_list_for_letter
