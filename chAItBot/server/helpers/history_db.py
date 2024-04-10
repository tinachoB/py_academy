"""
Cache using Redis
"""
import datetime
import json
from typing import List, cast

from server.common.common import create_redis_connection
from server.common.env_variables import RedisEnvVars
from server.common.singleton import Singleton

HistoryCacheItem = List[str]
HistoryCache = List[HistoryCacheItem]

EXPIRATION_TIME = 30  # Minutes


class HistoryDB(metaclass=Singleton):
    """
    Class used to represent a History DB Singleton instance.
    """

    def __init__(
        self: "HistoryDB", config: RedisEnvVars, expiration_time: int = EXPIRATION_TIME
    ) -> None:
        """
        Default class constructor
        :param config: Env vars needed to connect against Redis DB.
        :param expiration_time: Default expiration time to persist information.
        :return: None
        """
        self._redis = create_redis_connection(config=config, db=config.history_db)
        self._expiration_time: datetime.timedelta = datetime.timedelta(minutes=expiration_time)

    def get(self: "HistoryDB", key: str) -> HistoryCache:
        """
        Gets the current history cache
        :param key: Specific key to get information from.
        :return: HistoryCache NT with all needed results.
        """
        response = self._redis.get(key)
        return cast(HistoryCache, json.loads(response)) if response is not None else []

    def set(self: "HistoryDB", key: str, value: HistoryCache) -> None:
        """
        Set a new history cache value
        :param key: Specific key to update information
        :param value: Specific value, associated with the key, to update information
        :return: None
        """
        self._redis.set(name=key, value=json.dumps(value), ex=self._expiration_time)
