"""
Common functionalities.
"""

from fastapi import HTTPException, status
from typing_extensions import Dict


def error_response(
    detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> HTTPException:
    """
    Error response method to return the appropriate NT with the information.
    :param detail: Message to be displayed as part of the error.
    :param status_code: The status code.
    :return: HTTPException object representing the error message.
    """
    return HTTPException(
        status_code=status_code,
        detail=detail,
    )


def error_detail(
    detail: str = "Internal server error details.",
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Error response method to return a custom message's detail through the API
    :param detail: Message to be displayed as part of the error.
    :return: Dict representing the custom error message.
    """
    return {
        "application/json": {
            "example": {
                "detail": detail,
            }
        }
    }
