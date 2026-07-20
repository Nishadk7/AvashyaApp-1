import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")


ALLOWED_TYPES = ["code", "pdf", "video", "image", "txt"]

class Item(Base):
    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    file_reference = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="items")
    tags = relationship("ItemTag", back_populates="item", cascade="all, delete-orphan")


class ItemTag(Base):
    __tablename__ = "item_tags"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    key = Column(String, nullable=False, index=True)
    value = Column(String, nullable=False, index=True)

    item = relationship("Item", back_populates="tags")
