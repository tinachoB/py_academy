from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship
from server.helpers.mysql_helper import ModelBase

class MessagesModel(ModelBase):  # type: ignore[misc]
    """
    Messages Data Base Model
    """

    __tablename__ = "messages"

    # Mapping between MySql table fields and sqlalchemy framework modeling
    Id = Column(Integer, primary_key=True, index=True)
    CategoryId = Column(Integer)
    MessageTypeCode = Column(String(100))
    Message = Column(String(500))
    LastDateModified = Column(DateTime)
    LastUserModifiedId = Column(Integer)