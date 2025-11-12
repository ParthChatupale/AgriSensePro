"""
Pydantic schemas for request/response validation.

These schemas define the structure of data sent to and received from the API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    userType: str = Field(alias="userType")

    class Config:
        populate_by_name = True
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    phone: Optional[str] = None
    userType: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

