import pymongo
from project.src.services.utilities.env_config import config
from project.src.core.interfaces.infrastructure_interfaces import MongoConnectionInterface


class MongoConnection(MongoConnectionInterface):
    connection: any = None

    @classmethod
    def get_singleton_connection(cls) -> pymongo.MongoClient:
        if cls.connection is None:
            try:
                # host = f'{config(MongoConnection)}'
                host = f"mongodb://{config('MONGO_USER')}:{config('MONGO_PASS')}@{config('MONGO_HOST')}:{config('MONGO_PORT')}"
                connection = pymongo.MongoClient(host)
                cls.connection = connection
            except Exception as error:
                raise error

        return cls.connection
