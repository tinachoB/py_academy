"""
Tests for the person class.
"""
from typing import Dict, Union

import pytest

from tests.assets.generator.output.person import Person
from tests.common_test_helpers import parametrize_wrapper


def test_default_constructor() -> None:
    """
    Tests the default constructor.
    :return: None.
    """
    p = Person()

    assert p.id == -1
    assert p.first_name == ""
    assert p.last_name == ""
    assert p.email is None


def test_constructor() -> None:
    p = Person(id=3, first_name="John", last_name="Smith", email="john.smith@something.com")

    assert p.id == 3
    assert p.first_name == "John"
    assert p.last_name == "Smith"
    assert p.email == "john.smith@something.com"


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            {
                "person_a": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "person_b": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "expected_result": True,
            },
            {
                "person_a": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "person_b": Person(
                    id=9, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "expected_result": False,
            },
            {
                "person_a": Person(
                    id=3, first_name="Peter", last_name="Smith", email="john.smith@something.com"
                ),
                "person_b": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "expected_result": False,
            },
            {
                "person_a": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "person_b": Person(
                    id=3, first_name="John", last_name="Taylor", email="john.smith@something.com"
                ),
                "expected_result": False,
            },
            {
                "person_a": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith@something.com"
                ),
                "person_b": Person(
                    id=3, first_name="John", last_name="Smith", email="john.smith_2@something.com"
                ),
                "expected_result": False,
            },
        ]
    )
)
def test_equal_operator(person_a: Person, person_b: Person, expected_result: bool) -> None:
    assert expected_result == (person_a == person_b)


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            {"fields": {"id": 3}, "expected_value": Person(id=3)},
            {
                "fields": {"id": 3, "first_name": "John", "last_name": "Smith"},
                "expected_value": Person(id=3, first_name="John", last_name="Smith"),
            },
            {
                "fields": {
                    "id": 3,
                    "first_name": "John",
                    "last_name": "Smith",
                    "email": "some@email.com",
                },
                "expected_value": Person(
                    id=3, first_name="John", last_name="Smith", email="some@email.com"
                ),
            },
            {
                "fields": {
                    "id": 3,
                    "first_name": "  John  ",
                    "last_name": "  Smith  ",
                    "email": "  some@email.com  ",
                },
                "expected_value": Person(
                    id=3, first_name="John", last_name="Smith", email="some@email.com"
                ),
            },
            {
                "fields": {"id": -1},
                "expected_value": ValueError("Invalid 'id' value"),
            },
            {
                "fields": {"last_name": None},
                "expected_value": ValueError("Invalid 'last_name' value"),
            },
            {
                "fields": {"last_name": "  "},
                "expected_value": ValueError("Invalid 'last_name' value"),
            },
            {
                "fields": {"first_name": None},
                "expected_value": ValueError("Invalid 'first_name' value"),
            },
            {
                "fields": {"first_name": "  "},
                "expected_value": ValueError("Invalid 'first_name' value"),
            },
        ]
    )
)
def test_setters(fields: Dict[str, str], expected_value: Union[ValueError, Person]) -> None:
    def set_properties():
        for property, value in fields.items():
            if property == "id":
                p.id = value
            if property == "first_name":
                p.first_name = value
            if property == "last_name":
                p.last_name = value
            if property == "email":
                p.email = value

    p = Person()

    if isinstance(expected_value, ValueError):
        with pytest.raises(ValueError) as e:
            set_properties()
        assert str(expected_value) in str(e)
    else:
        set_properties()
        assert p == expected_value
