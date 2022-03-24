import pymongo
from src.services.utilities.env_config import config
from src.core.interfaces.infrastructure_interfaces import MongoConnectionInterface


class MongoConnection(MongoConnectionInterface):
    connection: any = None

    @classmethod
    def get_singleton_connection(cls) -> pymongo.MongoClient:
        if cls.connection is None:
            try:
                host = f"mongodb://{config('MONGO_USER')}:{config('MONGO_PASS')}@{config('MONGO_HOST')}:{config('MONGO_PORT')}"
                # host = config('HOST_CONNECTION')
                connection = pymongo.MongoClient(host)
                cls.connection = connection
            except Exception as error:
                raise error

        return cls.connection
