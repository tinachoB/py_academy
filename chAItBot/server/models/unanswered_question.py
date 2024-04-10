"""
Model for the Unanswered Question table
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase


class UnansweredQuestionModel(ModelBase):  # type: ignore[misc]
    """
    Unanswered Question Model
    """

    __tablename__ = "questionwithoutanswer"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    id = Column(Integer, primary_key=True, index=True)
    Content = Column(String(768))
    Resolved = Column(Boolean)
    CreatedOn = Column(DateTime)

    history_detail = relationship("HistoryDetailModel", back_populates="question")

    question_category = relationship(
        "QuestionWithoutAnswersCategoriesModel", back_populates="questions", cascade="all, delete-orphan"
    )

