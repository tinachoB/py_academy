"""
Model for the Unanswered Question table
"""
from server.models.documentrelateddata import DocumentRelatedDataModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel


class DocumentModel(ModelBase):  # type: ignore[misc]
    """
    Knowledge Data Base Model
    """

    __tablename__ = "document"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100))
    FileName = Column(String(100))
    Description = Column(String(200))
    UploadDate = Column(DateTime)

    Contenido = relationship(
        "DocumentRelatedDataModel", back_populates="document", cascade="all, delete-orphan"
    )

    document_category = relationship(
        "DocumentsCategoriesModel", back_populates="document", cascade="all, delete-orphan"
    )
