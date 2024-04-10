"""
Models used as parameters and responses.
"""
from typing import List

from fastapi import status
from pydantic import BaseModel, Field


class Question(BaseModel):
    """
    Class to represent the Question to be used in the bot
    """

    question: str = Field(
        description="The question asked by the user",
        example="What services do you provide?"
    )
    categoriesId: List[int] = Field(
        description="The knowledge base categories to be used.",
        example=[1],
        min_items=1
    )
    session_id: str = Field(
        description="The current session id.",
        example="bec5420b-5972-11ee-b5b2-5405dbfa016b",
        default="",
    )


class DatabaseResponse(BaseModel):
    """
    Class to represent the Database Response information
    """

    status: int = Field(
        default=status.HTTP_200_OK,
        description="The status code returned by the server.",
        example=200,
    )
    modified_values: int = Field(
        description="The number of modified values in the DB.",
        default=0,
        example=2,
    )
    unmodified_values: int = Field(
        description="The number of values not modified in the DB.",
        default=0,
        example=1,
    )
    description: str = Field(
        description="Some description message about the taken action.",
        default="",
        example="",
    )


class DeleteDatabaseResponse(BaseModel):
    """
    Class to represent the Deletion Database Response
    """

    status: int = Field(
        default=status.HTTP_200_OK,
        description="The status code returned by the server.",
        example=200,
    )
    description: str = Field(
        description="Some description message about the taken action.",
        default="",
        example="",
    )


class BotStatus(BaseModel):
    """
    Class to represent the bot status message.
    """

    status: int = Field(
        default=status.HTTP_200_OK,
        description="The status code returned by the server.",
        example=200,
    )
    knowledge_database_size: int = Field(
        default=0,
        description="The size of the knowledge database.",
        example=153,
    )
    unanswered_questions_size: int = Field(
        default=0,
        description="The number of unanswered questions.",
        example=23,
    )


class BotStatisticsItem(BaseModel):
    tokens: int = Field(
        default=0,
        description="The number of tokens being used by the bot.",
        example=0,
    )
    charges: float = Field(
        default=0.0,
        description="The current charges (U$D).",
        example=0.0043,
    )


class CompletionsBotStatistics(BaseModel):
    input: BotStatisticsItem = Field(
        default=BotStatisticsItem(),
        description="The current input completion stats",
    )
    output: BotStatisticsItem = Field(
        default=BotStatisticsItem(),
        description="The current output completion stats",
    )
    total: BotStatisticsItem = Field(
        default=BotStatisticsItem(),
        description="The current total completion stats",
    )


class BotStatistics(BaseModel):
    """
    Class to represent the bot stats message.
    """

    status: int = Field(
        default=status.HTTP_200_OK,
        description="The status code returned by the server.",
        example=200,
    )
    questions_count: int = Field(
        default=0,
        description="The number of questions asked to the bot.",
        example=25,
    )
    embeddings: BotStatisticsItem = BotStatisticsItem()
    completions: CompletionsBotStatistics = CompletionsBotStatistics()


class Data(BaseModel):
    status: int = Field(
        default=status.HTTP_200_OK,
        description="The status code returned by the server.",
        example=200,
    )
    session_id: str = Field(
        ..., description="The current session id", example="bec5420b-5972-11ee-b5b2-5405dbfa016b"
    )
    answer: str = Field(..., description="The answer returned by the chat-bot", example="")


class BotResponse(BaseModel):
    data: Data
