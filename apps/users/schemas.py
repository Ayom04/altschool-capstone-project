from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re
from apps.users.models import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password must contain uppercase, lowercase, number and special character"
    )
    role: UserRole = UserRole.STUDENT

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Validate password strength

        Requirements:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character (@$!%*?&)
        """
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[@$!%*?&]", value):
            raise ValueError(
                "Password must contain at least one special character (@$!%*?&)")

        return value

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate role is a valid UserRole"""
        if v not in [UserRole.STUDENT, UserRole.ADMIN]:
            raise ValueError('Role must be either student or admin')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class EnrolledCourse(BaseModel):
    """Nested course data in user"""
    id: int
    title: str
    code: str
    capacity: int

    model_config = {
        "from_attributes": True
    }


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserWithEnrollments(UserBase):
    """Schema for user with enrolled courses"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    enrollments: List[EnrolledCourse] = []

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    email: Optional[str] = None
    role: Optional[str] = None
