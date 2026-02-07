from sqlalchemy import Column, DateTime, Integer, String, Boolean, func
from sqlalchemy.orm import relationship
from apps.config.database import Base


class Course(Base):
    """Course model representing courses in the system"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
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
        "Enrollment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course(id={self.id}, code={self.code}, title={self.title})>"

    @property
    def enrolled_count(self):
        """Get count of enrolled students"""
        return len(self.enrollments)

    @property
    def is_full(self):
        """Check if course is at capacity"""
        return self.enrolled_count >= self.capacity

    def to_dict(self, include_enrollments=False):
        """Convert course to dictionary representation"""
        data = {
            "id": self.id,
            "title": self.title,
            "code": self.code,
            "capacity": self.capacity,
            "is_active": self.is_active,
            "enrolled_count": self.enrolled_count,
            "is_full": self.is_full,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_enrollments:
            data["enrollments"] = [
                {
                    "id": e.user.id,
                    "name": e.user.name,
                    "email": e.user.email
                } for e in self.enrollments
            ]

        return data
