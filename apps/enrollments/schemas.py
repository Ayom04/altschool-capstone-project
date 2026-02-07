from pydantic import BaseModel
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.schemas import UserResponse
    from apps.courses.schemas import CourseResponse


class EnrollmentCreate(BaseModel):
    """Schema for creating an enrollment"""
    course_id: int


class UserInEnrollment(BaseModel):
    """Nested user data in enrollment"""
    id: int
    name: str
    email: str
    role: str

    model_config = {
        "from_attributes": True
    }


class CourseInEnrollment(BaseModel):
    """Nested course data in enrollment"""
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class EnrollmentResponse(BaseModel):
    """Schema for enrollment response with full relationship data"""
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    user: UserInEnrollment
    course: CourseInEnrollment

    model_config = {
        "from_attributes": True
    }


class EnrollmentWithDetails(BaseModel):
    """Schema for enrollment with user and course details"""
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    user: UserInEnrollment
    course: CourseInEnrollment

    model_config = {
        "from_attributes": True
    }
