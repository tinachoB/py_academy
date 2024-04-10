"""
Model for the KnowledgeBaseCategories table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase


class KnowledgeBaseCategoriesModel(ModelBase):  # type: ignore[misc]
    """
    KnowledgeBaseCategories Data Base Model
    """

    __tablename__ = "knowledgebasecategories"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    KnowledgeBase_Id = Column(Integer, ForeignKey("knowledgebase.Id"))
    Category_Id = Column(Integer, ForeignKey("category.Id"))

    categories = relationship(
        "CategoriesModel",
        foreign_keys=[Category_Id],
        back_populates="category_knowledge"
    )
    knowledges = relationship(
        "KnowledgeDataBaseModel",
        foreign_keys=[KnowledgeBase_Id],
        back_populates="knowledge_category",
    )
