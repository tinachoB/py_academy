"""
Class used to measure the elapsed time between two events.
"""
import datetime


class ElapsedTime:
    __TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self: "ElapsedTime"):
        self.__start_time: datetime.datetime = datetime.datetime.now()
        self.__end_time: datetime.datetime = self.__start_time

    def start(self: "ElapsedTime") -> str:
        self.__start_time = datetime.datetime.now()
        return self.__start_time.strftime(self.__TIME_FORMAT)

    def end(self: "ElapsedTime") -> str:
        self.__end_time = datetime.datetime.now()
        return self.__end_time.strftime(self.__TIME_FORMAT)

    @property
    def elapsed(self: "ElapsedTime") -> str:
        td = self.__end_time - self.__start_time
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
