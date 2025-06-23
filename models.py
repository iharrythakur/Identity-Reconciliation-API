from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.sql import func
from database import Base
import enum


class LinkPrecedence(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    linkedId = Column(Integer, nullable=True, index=True)
    linkPrecedence = Column(Enum(LinkPrecedence),
                            nullable=False, default=LinkPrecedence.PRIMARY)
    createdAt = Column(DateTime(timezone=True),
                       server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)
    deletedAt = Column(DateTime(timezone=True), nullable=True)
