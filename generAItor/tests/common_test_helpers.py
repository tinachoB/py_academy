"""
Functions used across tests
"""
from functools import singledispatch
from itertools import zip_longest
from typing import Any, Callable, Dict, List, Union

from pytest_mock import MockFixture
from typing_extensions import TypedDict

AnyFunction = Callable[..., Any]  # type: ignore


class Parametrize(TypedDict):  # pylint: disable=too-few-public-methods
    """Represents the named parameters passed to pytest.mark.parametrize"""

    argnames: str
    argvalues: List[List[Any]]


def function_import_path(func: AnyFunction) -> str:
    """
    Stringify the import path of a function for patching.

    :param func: function to analyze
    :return: import path of the function as a string
    """
    return f"{func.__module__}.{func.__name__}"


def parametrize_wrapper(kwarg_dict_list: List[Dict[str, Any]]) -> Parametrize:  # type: ignore[misc]
    """ ""
    Wrap a list of keyword argument dictionaries into a form understandable to parametrize. This
    makes long lists of parametrized arguments easier to read at the price of more verbose dicts
    kwargs.

    :param kwarg_dict_list: A list of keyword argument dictionaries
    :return: Parametrize
    """
    # kwarg_dict_list must not be empty
    assert kwarg_dict_list
    # assert all keyword args are in the same order and the same length
    assert all(
        all(i == x[0] for i in x[1:]) for x in zip_longest(*(d.keys() for d in kwarg_dict_list))
    )
    return Parametrize(
        # since all list elements have the same parameters, just use the kwargs from the head
        argnames=",".join(kwarg_dict_list[0].keys()),
        argvalues=[list(d.values()) for d in kwarg_dict_list],
    )


def patch_function_with_exception(  # type: ignore
    mocker: MockFixture,
    func: AnyFunction,
    mocked_value: Union[Any, Exception],
) -> MockFixture._Patcher:  # pylint: disable=protected-access
    """
    This function sets the value to be returned or the exception to be thrown according
    to the mocked value. To accomplish this it uses 'type dispatching'.
    If the mocked value is an exception, the 'side_effect' of the mocker is set. Otherwise
    the 'return_value' is used.
    :param mocker: The mocker to be set.
    :param func: The function to be mocked.
    :param mocked_value: The value to be set as a return_value or a side_effect.
    :return MockFixture._Patcher:  The mock object.
    """

    @singledispatch
    def _set_mocked_value(value: Any) -> MockFixture._Patcher:  # type: ignore
        # pylint: disable=protected-access
        """
        This function sets the value to be returned by the mocked function.
        :param value: The value to be set.
        :return: None
        """
        return mocker.patch(
            function_import_path(func),
            return_value=value,
        )

    @_set_mocked_value.register(Exception)
    def _set_exception_mocked_value(value: Exception) -> MockFixture._Patcher:
        # pylint: disable=protected-access
        """
        This function sets the exception to be thrown by the mocked function.
        :param value: The exception to be thrown.
        :return: None
        """
        return mocker.patch(
            function_import_path(func),
            side_effect=value,
        )

    return _set_mocked_value(mocked_value)


def patch_object_with_exception(  # type: ignore
    mocker: MockFixture,
    obj: type,
    member_func: str,
    mocked_value: Union[Any, BaseException],
) -> MockFixture._Patcher:  # pylint: disable=protected-access
    """
    This function sets the value to be returned or the exception to be thrown by an object
    according to the mocked value. To accomplish this it uses 'type dispatching'.
    If the mocked value is an exception, the 'side_effect' of the mocker is set. Otherwise
    the 'return_value' is used.
    :param mocker: The mocker to be set.
    :param obj: The object with the function we want to mock.
    :param member_func: The member function to be mocked.
    :param mocked_value: The value to be set as a return_value or a side_effect.
    :return MockFixture._Patcher:  The mock object.
    """

    @singledispatch
    def _set_mocked_value(value: Any) -> MockFixture._Patcher:  # type: ignore
        # pylint: disable=protected-access
        """
        This function sets the value to be returned by the mocked function.
        :param value: The value to be set.
        :return: None
        """
        return mocker.patch.object(
            obj,
            member_func,
            return_value=value,
        )

    @_set_mocked_value.register(BaseException)
    def _set_exception_mocked_value(value: BaseException) -> MockFixture._Patcher:
        # pylint: disable=protected-access
        """
        This function sets the exception to be thrown by the mocked function.
        :param value: The exception to be thrown.
        :return: None
        """
        return mocker.patch.object(
            obj,
            member_func,
            side_effect=value,
        )

    return _set_mocked_value(mocked_value)
