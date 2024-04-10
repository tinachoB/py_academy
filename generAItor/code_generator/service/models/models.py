"""
Models used as parameters and responses.
"""

from fastapi import status
from pydantic import BaseModel, Field


class Data(BaseModel):  # type: ignore[misc]
    status: int = Field(
        default=status.HTTP_200_OK,
        description="The status code returned by the server.",
        examples=[200],
    )
    answer: str = Field(..., description="The answer returned by the code generator", examples=[""])


class CodeGeneratorResponse(BaseModel):  # type: ignore[misc]
    data: Data
