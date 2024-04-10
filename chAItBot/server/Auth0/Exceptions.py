from fastapi import HTTPException, status

detail = "Not authorized"


class UnauthorizedException(HTTPException):

    def __init__(self, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail
        )