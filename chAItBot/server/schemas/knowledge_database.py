import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, conint, constr, Field

from server.helpers.openai_helper import NumpyArray
from server.schemas.wrappers.base_response import MessagePost


class Categories(BaseModel):
    id: int
    description: str


class Knowledge(BaseModel):
    id: int
    title: str
    content: str
    categories: List[Categories]


class KnowledgeDataBaseResponse(BaseModel):
    data: Union[Knowledge, dict]
    message: MessagePost


class KnowledgeBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    content: constr(strip_whitespace=True, min_length=1)
    categories: List[int] = Field(..., min_items=1)
    documentId: int
    relatedQuestionId: Optional[int] = None


class UploadKnowledgeBase(BaseModel):
    id: int = Field(..., gt=0)
    title: constr(strip_whitespace=True, min_length=1)
    content: constr(strip_whitespace=True, min_length=1)
    categories: List[int] = Field(..., min_items=1)




class KnowledgeBaseRequest(BaseModel):
    knowledgeBase: KnowledgeBase


class UploadKnowledgeBaseRequest(BaseModel):
    knowledgeBase: UploadKnowledgeBase


class Pagination(BaseModel):
    totalRecords: int
    page: int
    pageSize: int
    totalPages: int


class GetKnowledgeBase(BaseModel):
    id: Optional[int] = None  # Optional because it's an autoincrement db value
    title: str
    content: str
    categories: List[Categories]


class GetKnowledgeBaseResponse(BaseModel):
    data: List[GetKnowledgeBase]
    pagination: Pagination
    message: MessagePost
