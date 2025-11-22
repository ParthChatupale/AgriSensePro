"""
SQLAlchemy ORM models.

Defines the `User` model used to store authentication information.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    user_type = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    crop = Column(String, nullable=True)  # Primary crop (cotton, wheat, rice, etc.)
    location = Column(String, nullable=True)  # Farm location
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    village = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to posts
    posts = relationship("Post", back_populates="author_user", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    region = Column(String, nullable=True)  # State/region of the author
    crop = Column(String, nullable=True)  # Crop type (rice, wheat, cotton, etc.)
    category = Column(String, nullable=True)  # Post category (tip, question, issue, success)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    image_url = Column(String, nullable=True)  # URL to uploaded image
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author_user = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("Post", back_populates="likes")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    post = relationship("Post", back_populates="comments")
