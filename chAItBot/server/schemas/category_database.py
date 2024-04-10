import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, constr, Field

from server.helpers.openai_helper import NumpyArray
from server.schemas.wrappers.base_response import MessagePost


class Category(BaseModel):
    id: Optional[int] = None  # Optional because it's an autoincrement db value
    description: str
    #: bool
    # CreateOn: datetime


class GetCategoryById(BaseModel):
    data: Union[Category, dict]
    message: MessagePost


class Pagination(BaseModel):
    totalRecords: int
    page: int
    pageSize: int
    totalPages: int


class CategoryResponse(BaseModel):
    data: List[Category]
    pagination: Pagination
    message: MessagePost


class CategoryRequest(BaseModel):
    description: constr(strip_whitespace=True, min_length=1)


class CategoryByIdRequest(BaseModel):
    id: int = Field(..., gt=0)
    description: constr(strip_whitespace=True, min_length=1)


class CategoryBaseByIdRequest(BaseModel):
    category: CategoryByIdRequest


class CategoryBaseRequest(BaseModel):
    category: CategoryRequest
