"""
Model for the Unanswered Question table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel


class KnowledgeDataBaseModel(ModelBase):  # type: ignore[misc]
    """
    Knowledge Data Base Model
    """

    __tablename__ = "knowledgebase"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True, index=True)
    Title = Column(String(100))
    Content = Column(String(768))
    CreatedOn = Column(DateTime)
    Embedding = Column(LargeBinary)
    DocumentId = Column(Integer)

    knowledge_category = relationship(
        "KnowledgeBaseCategoriesModel", back_populates="knowledges", cascade="all, delete-orphan"
    )
