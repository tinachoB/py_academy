import datetime
from typing import Optional

from pydantic import BaseModel


class NoResultsResponse(BaseModel):
    message: str
