from typing import Optional, List, TypeVar

from fastapi import UploadFile, File
from pydantic import BaseModel

T = TypeVar('T')


class document_request(BaseModel):
    name: str
    filename: str
    description: Optional[str] = None
    file: str


class document_with_errorsSchema(BaseModel):
    title: str
    content: str
    message: str

class document_response(BaseModel):
    documentId: int

class document_save_data(BaseModel):
    id: int
    categories: List[int]
