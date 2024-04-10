"""
Model for the Unanswered Question table
"""
from server.models.documentrelateddata import DocumentRelatedDataModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel


class DocumentsCategoriesModel(ModelBase):  # type: ignore[misc]
    """
    Knowledge Data Base Model
    """

    __tablename__ = "documentscategories"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    DocumentId = Column(Integer, ForeignKey("document.Id"))
    CategoryId = Column(Integer, ForeignKey("category.Id"))

    categories = relationship(
        "CategoriesModel",
        foreign_keys=[CategoryId],
        back_populates="category_document"
    )

    document = relationship(
        "DocumentModel",
        foreign_keys=[DocumentId],
        back_populates="document_category"
    )