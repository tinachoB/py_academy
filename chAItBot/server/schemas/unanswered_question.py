"""
Schema for the Unanswered Question APIs
"""
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from server.schemas.wrappers.base_response import MessagePost


class Categories(BaseModel):
    id: int
    description: str


class UnansweredQuestion(BaseModel):
    id: Optional[int] = None  # Optional because it's an autoincrement db value
    content: str
    resolved: bool
    createdOn: str
    categories: List[Categories]


class Pagination(BaseModel):
    totalRecords: int
    page: int
    pageSize: int
    totalPages: int


class UnansweredQuestionRequest(BaseModel):
    content: int
    resolve: bool


class GetUnansweredQuestionById(BaseModel):
    data: Union[UnansweredQuestion, dict]
    message: MessagePost


class Result(BaseModel):
    success: bool


class QuestionResponse(BaseModel):
    result: Result


class UnansweredQuestionResponse(BaseModel):
    data: List[UnansweredQuestion]
    pagination: Pagination
    message: MessagePost

    class Config:
        from_attributes = True


class GetHistoryDetailResponse(BaseModel):
    id: int
    question: str
    answer: str
    createdOn: str
