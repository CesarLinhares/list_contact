from abc import ABC, abstractmethod


class InterfaceMongo(ABC):
    DATABASE: str
    COLLECTION: str

    @abstractmethod
    def insert_one(self, data: dict) -> bool:
        pass

    @abstractmethod
    def update_one(self, identity: str, fields_to_update: dict) -> bool:
        pass

    @abstractmethod
    def find_all(self, filter_fields: dict = {}) -> list:
        pass

    @abstractmethod
    def find(self, filter_fields: dict = {}) -> list:
        pass

    @abstractmethod
    def find_one(self, identity: str, filter_fields: dict = {}) -> dict:
        pass

    @abstractmethod
    def aggregate(self, pipeline: list) -> dict:
        pass

    @abstractmethod
    def delete_one(self, identity: str) -> bool:
        pass


class InterfaceRedis(ABC):
    @abstractmethod
    def insert(self, key: str) -> bool:
        pass

    @abstractmethod
    def exclude(self, key: str) -> bool:
        pass

    @abstractmethod
    def verify_if_exists(self, key: str) -> bool:
        pass
