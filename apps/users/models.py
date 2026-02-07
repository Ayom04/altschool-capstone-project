from sqlalchemy import Column, DateTime, Integer, String, Boolean, Enum, func
from sqlalchemy.orm import relationship
from apps.config.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    ADMIN = "admin"


class User(Base):
    """User model representing system users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    enrollments = relationship(
        "Enrollment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self, include_enrollments=False):
        """Convert user to dictionary representation (excludes hashed_password)"""
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_enrollments:
            data["enrollments"] = [
                {
                    "id": e.course.id,
                    "title": e.course.title,
                    "code": e.course.code,
                    "capacity": e.course.capacity
                } for e in self.enrollments
            ]

        return data

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
