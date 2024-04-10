"""
Unanswered DB using Redis
"""
from datetime import datetime
from typing import List

from server.common.common import create_redis_connection
from server.common.env_variables import RedisEnvVars
from server.common.singleton import Singleton


class UnansweredQuestionsDB(metaclass=Singleton):
    """
    Class representing the Unanswered Question DB information and methods.
    """

    def __init__(self: "UnansweredQuestionsDB", config: RedisEnvVars) -> None:
        """
        Default class constructor
        :param config: Redis env vars to connect to the DB.
        :return: None
        """
        self._redis = create_redis_connection(config=config, db=config.unanswered_questions_db)

    def clear(self: "UnansweredQuestionsDB") -> int:
        """
        Clears the entire Unanswered Question DB.
        :return: Amount of keys deleted.
        """
        keys = list(self._redis.scan_iter("q:*"))
        for key in keys:
            self._redis.delete(key)
        return len(keys)

    def get_list(self: "UnansweredQuestionsDB") -> List[str]:
        """
        Gets the current unanswered questions
        :return: the current unanswered questions
        """
        return [self._redis.get(key) for key in self._redis.scan_iter("q:*")]

    def set(self: "UnansweredQuestionsDB", question: str) -> None:
        """
        Sets a new question to the DB.
        :param question: Question to update the DB with.
        :return: None
        """
        self._redis.set(name=f"q:{datetime.now().timestamp()}", value=question)

    @property
    def size(self: "UnansweredQuestionsDB") -> int:
        """
        Gets the current DB size
        :return: the current DB size
        """
        return self._redis.dbsize()
