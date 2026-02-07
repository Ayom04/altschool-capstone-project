from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.config.database import Base


class Enrollment(Base):
    """Enrollment model representing student-course relationships"""
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey(
        "courses.id", ondelete="CASCADE"), nullable=False)
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
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id})>"

    def to_dict(self, include_relations=True):
        """Convert enrollment to dictionary representation"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_relations:
            data["user"] = {
                "id": self.user.id,
                "name": self.user.name,
                "email": self.user.email,
                "role": self.user.role.value
            }
            data["course"] = {
                "id": self.course.id,
                "title": self.course.title,
                "code": self.course.code,
                "capacity": self.course.capacity,
                "is_active": self.course.is_active
            }

        return data
