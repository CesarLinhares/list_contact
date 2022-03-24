from abc import ABC, abstractmethod


class MongoConnectionInterface(ABC):
    connection: any

    @classmethod
    @abstractmethod
    def get_singleton_connection(cls) -> any:
        pass


class RedisConnectionInterface(ABC):
    connection: any

    @classmethod
    @abstractmethod
    def get_singleton_connection(cls) -> any:
        pass
