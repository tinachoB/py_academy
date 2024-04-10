"""
Model for the KnowledgeBaseCategories table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase


class QuestionWithoutAnswersCategoriesModel(ModelBase):  # type: ignore[misc]
    """
    KnowledgeBaseCategories Data Base Model
    """

    __tablename__ = "questionswithoutanswercategories"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    questionId = Column(Integer, ForeignKey("questionwithoutanswer.id"))
    categoryId = Column(Integer, ForeignKey("category.Id"))

    categories = relationship(
        "CategoriesModel",
        foreign_keys=[categoryId],
        back_populates="category_question"
    )
    questions = relationship(
        "UnansweredQuestionModel",
        foreign_keys=[questionId],
        back_populates="question_category",
    )
