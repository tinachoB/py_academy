"""
Class used to define the Person class.
"""
from typing import Optional


class Person:

    MAX_FIRST_NAME_LENGTH = 40
    MAX_LAST_NAME_LENGTH = 40

    def __init__(
        self: "Person",
        id: int = -1,
        first_name: str = "",
        last_name: str = "",
        email: Optional[str] = None,
    ) -> None:
        """
        Constructor.
        :param id: The id of the record.
        :param first_name:  The first name of the person.
        :param last_name: The last name of the person.
        :param email: The email of the person.
        :return: None.
        """
        self.__id: int = id
        self.__first_name: str = first_name
        self.__last_name: str = last_name
        self.__email: Optional[str] = email

    @property
    def id(self: "Person") -> int:
        """
        Gets the id.
        :return: The id.
        """
        return self.__id

    @property
    def first_name(self: "Person") -> str:
        """
        Gets the first name.
        :return: The first name.
        """
        return self.__first_name

    @property
    def last_name(self: "Person") -> str:
        """
        Gets the last name.
        :return: The last name.
        """
        return self.__last_name

    @property
    def email(self: "Person") -> Optional[str]:
        """
        Gets the email.
        :return: The email.
        """
        return self.__email

    @id.setter
    def id(self: "Person", id: int) -> None:
        """
        Sets the id.
        :param id: The value to be set.
        :raise: ValueError if some error in the value is found.
        :return: None.
        """
        if id >= 0:
            self.__id = id
        else:
            raise ValueError("Invalid 'id' value.")

    @first_name.setter
    def first_name(self: "Person", first_name: str) -> None:
        """
        Sets the first name.
        :param first_name: The value to be set.
        :raise: ValueError if some error in the value is found.
        :return: None.
        """
        if first_name is not None and 0 < len(first_name.strip()) <= self.MAX_FIRST_NAME_LENGTH:
            self.__first_name = first_name.strip()
        else:
            raise ValueError("Invalid 'first_name' value.")

    @last_name.setter
    def last_name(self: "Person", last_name: str) -> None:
        """
        Sets the last name.
        :param last_name: The value to be set.
        :raise: ValueError if some error in the value is found.
        :return: None.
        """
        if last_name is not None and 0 < len(last_name.strip()) <= self.MAX_LAST_NAME_LENGTH:
            self.__last_name = last_name.strip()
        else:
            raise ValueError("Invalid 'last_name' value.")

    @email.setter
    def email(self: "Person", email: str) -> None:
        """
        Sets the email.
        :param email: The value to be set.
        :return: None.
        """
        if email is not None:
            self.__email = email.strip()

    def __eq__(self: "Person", other: "Person") -> bool:
        """
        Checks for equality with another object.
        :param other: The object to be compared with.
        :return: True if the `other` object is equal to this one,
        false otherwise.
        """
        return (
            self.id == other.id
            and self.last_name == other.last_name
            and self.first_name == other.first_name
            and self.email == other.email
        )
