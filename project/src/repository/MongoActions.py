from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from project.src.core.interfaces.repository_interfaces import InterfaceMongo


class MongoActions(InterfaceMongo):
    DATABASE: str
    COLLECTION: str

    def __init__(self, infrastructure: MongoClient):
        connection = infrastructure
        database = connection[self.DATABASE]
        self.collection = database[self.COLLECTION]

    def insert_one(self, data: dict) -> bool:
        try:
            if not self.collection.insert_one(data):
                return False
            return True
        except DuplicateKeyError:
            return False

    def update_one(self, identity: str, fields_to_update: dict) -> bool:
        update_result = self.collection.update_one({"_id": identity}, {"$set": fields_to_update})
        return update_result.modified_count > 0

    def find_all(self, filter_fields: dict = {}) -> list:
        return self.collection.find(filter_fields)

    def find(self, filter_fields: dict = {}) -> list:
        return self.collection.find(filter_fields)

    def find_one(self, identity: str, filter_fields: dict = {}) -> dict:
        return self.collection.find_one({"_id": identity, **filter_fields})

    def aggregate(self, pipeline: list) -> dict:
        pass

    def delete_one(self, identity: str) -> bool:
        if not self.collection.find_one_and_delete({"_id": identity}):
            return False
        return True
