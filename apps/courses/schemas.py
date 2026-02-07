from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class CourseBase(BaseModel):
    """Base course schema with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., gt=0)


class CourseCreate(CourseBase):
    """Schema for creating a course"""

    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, v):
        """Validate capacity is greater than zero"""
        if v <= 0:
            raise ValueError('Capacity must be greater than zero')
        return v


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, v):
        """Validate capacity is greater than zero if provided"""
        if v is not None and v <= 0:
            raise ValueError('Capacity must be greater than zero')
        return v


class EnrolledStudent(BaseModel):
    """Nested student data in course"""
    id: int
    name: str
    email: str

    model_config = {
        "from_attributes": True
    }


class CourseResponse(CourseBase):
    """Schema for course response"""
    id: int
    is_active: bool
    enrolled_count: int = 0
    is_full: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CourseWithEnrollments(CourseBase):
    """Schema for course with enrolled students"""
    id: int
    is_active: bool
    enrolled_count: int = 0
    is_full: bool = False
    created_at: datetime
    updated_at: datetime
    enrollments: List[EnrolledStudent] = []

    model_config = {
        "from_attributes": True
    }
