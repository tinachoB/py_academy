"""
Model for the History table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.unanswered_question import UnansweredQuestionModel


class HistoryModel(ModelBase):  # type: ignore[misc]
    """
    Category Data Base Model
    """

    __tablename__ = "history"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    CreateOn = Column(DateTime)
    Session = Column(String(500))

    history_details = relationship("HistoryDetailModel", back_populates="history", cascade="all, delete-orphan",)