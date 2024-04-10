"""
Model for the Categories table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.questionwithoutanswers_categories_model import QuestionWithoutAnswersCategoriesModel
from server.models.unanswered_question import UnansweredQuestionModel
from server.models.documentscategories import DocumentsCategoriesModel


class CategoriesModel(ModelBase):  # type: ignore[misc]
    """
    Category Data Base Model
    """

    __tablename__ = "category"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    Description = Column(String(100))

    category_knowledge = relationship(
        "KnowledgeBaseCategoriesModel",
        foreign_keys=[KnowledgeBaseCategoriesModel.Category_Id],
        back_populates="categories",
    )

    category_question = relationship(
        "QuestionWithoutAnswersCategoriesModel",
        foreign_keys=[QuestionWithoutAnswersCategoriesModel.categoryId],
        back_populates="categories",
    )

    category_document = relationship(
        "DocumentsCategoriesModel",
        foreign_keys=[DocumentsCategoriesModel.CategoryId],
        back_populates="categories",
    )