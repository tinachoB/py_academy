"""
Model for the KnowledgeBaseCategories table
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import relationship

from server.helpers.mysql_helper import ModelBase


class DocumentRelatedDataModel(ModelBase):  # type: ignore[misc]
    """
    KnowledgeBaseCategories Data Base Model
    """

    __tablename__ = "documentrelateddata"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True)
    Title = Column(Text)
    Content = Column(Text)
    DocumentId = Column(Integer, ForeignKey("document.Id"))
    Status = Column(Integer)

    document = relationship(
        "DocumentModel", foreign_keys=[DocumentId], back_populates="Contenido"
    )
