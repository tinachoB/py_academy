"""
Model for the History Detail table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.unanswered_question import UnansweredQuestionModel


class HistoryDetailModel(ModelBase):  # type: ignore[misc]
    """
    Category Data Base Model
    """

    __tablename__ = "historydetail"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    Question = Column(String(768))
    Answer = Column(String(768))
    CreateOn = Column(DateTime)
    History_Id = Column(Integer, ForeignKey("history.Id"))
    QuestionWithoutAnswer_Id = Column(Integer, ForeignKey("questionwithoutanswer.id"))

    history = relationship("HistoryModel", back_populates="history_details")

    question = relationship(
        "UnansweredQuestionModel",
        foreign_keys=[QuestionWithoutAnswer_Id],
        back_populates="history_detail",
    )
