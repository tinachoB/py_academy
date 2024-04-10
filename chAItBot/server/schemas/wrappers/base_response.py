from typing import List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class MessagePost(BaseModel):
    status_code: int = 200
    message: str = "Ejecución exitosa."
    errors: List[str] = []


class TResponseDataPost(BaseModel):
    success: bool = True
    message: MessagePost = MessagePost()


class TResponseDataGet(BaseModel):
    data: T = None
    message: MessagePost = MessagePost()
