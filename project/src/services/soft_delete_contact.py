from pymongo import MongoClient
from redis import Redis

from project.src.core.entities import Active
from project.src.core.enum.status import Status
from project.src.core import IDelete
from project.src.repository import GetContactDetailsContactsRepository
from project.src.repository import SoftDeleteRegisters
from project.src.repository import UpdateContactRepository


class DeleteContact(IDelete):
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

    def delete(self, contact_id: str) -> dict:
        update_repository = UpdateContactRepository(self.mongo_infrastructure)
        mongo_repository = GetContactDetailsContactsRepository(self.mongo_infrastructure)
        contact = mongo_repository.get(contact_id)
        if not contact:
            return {'status': self.status_alias.get(False)}
        add_to_redis = self.redis_repository.add_contact_to_redis(contact)
        update_repository.update_contact(contact_id, [Active(is_active=False)])
        return {'status': self.status_alias.get(update_repository and add_to_redis)}
