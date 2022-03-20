from redis.client import Redis

from project.src.core.interfaces.infrastructure_interfaces import RedisConnectionInterface
from project.src.services.utilities.env_config import config


class RedisConnection(RedisConnectionInterface):
    connection: any = None

    @classmethod
    def get_singleton_connection(cls) -> Redis:
        if cls.connection is None:
            try:
                connection = Redis(
                    host=config("REDIS_HOST"),
                    port=config("REDIS_PORT"),
                    password=config("REDIS_PASS"),
                    db=config("REDIS_DB"))

                cls.connection = connection

            except Exception as error:
                raise error

        return cls.connection
