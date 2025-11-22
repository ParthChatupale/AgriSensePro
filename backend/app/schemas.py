"""
Pydantic schemas for request/response validation.

These schemas define the structure of data sent to and received from the API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    userType: str = Field(alias="userType")
    crop: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    crop: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: int
    phone: Optional[str] = None
    userType: Optional[str] = None
    crop: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================================
# Community/Post Schemas
# ============================================================================

class PostBase(BaseModel):
    content: str
    region: Optional[str] = None
    crop: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    content: Optional[str] = None
    crop: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class PostAuthor(BaseModel):
    id: int
    name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True


class PostOut(PostBase):
    id: int
    author_id: int
    author: Optional[PostAuthor] = None
    author_name: Optional[str] = None  # For backward compatibility
    region: Optional[str] = None
    crop: Optional[str] = None
    category: Optional[str] = None
    likes_count: int
    comments_count: int
    created_at: datetime
    is_liked: bool = False  # Whether current user liked this post

    class Config:
        from_attributes = True


class PostLikeCreate(BaseModel):
    post_id: int


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    author_name: Optional[str] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

