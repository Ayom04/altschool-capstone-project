from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from apps.config.database import get_db
from apps.courses.models import Course
from apps.courses.schemas import CourseCreate, CourseUpdate
from apps.users.models import User
from apps.common.security import require_admin
from apps.common.responses import success_response

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("")
def get_all_courses(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    Get all courses with optional filtering and pagination.
    
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - search: Search courses by title or code (case-insensitive)
    - is_active: Filter by active status (true/false)
    """
    # Limit max page size
    limit = min(limit, 1000)
    
    query = db.query(Course)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Course.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Course.title.ilike(search_term)) | (Course.code.ilike(search_term))
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    courses = query.offset(skip).limit(limit).all()
    
    return success_response(
        data={
            "items": [c.to_dict() for c in courses],
            "total": total,
            "skip": skip,
            "limit": limit
        },
        message="Courses retrieved"
    )


@router.get("/{course_id}", response_model=None)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return success_response(data=course.to_dict(), message="Course retrieved")


@router.get("/{course_id}/with-students", response_model=None)
def get_course_with_students(course_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Get course with enrolled students (admin only)"""
    course_with_enrollments = db.query(Course).options(
        joinedload(Course.enrollments)
    ).filter(Course.id == course_id).first()

    if not course_with_enrollments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return success_response(data=course_with_enrollments.to_dict(include_enrollments=True), message="Course with students retrieved")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_course(course_data: CourseCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(Course).filter(Course.code == course_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Course code already exists")
    new_course = Course(title=course_data.title, code=course_data.code,
                        capacity=course_data.capacity, is_active=True)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return success_response(data=new_course.to_dict(), message="Course created")


@router.put("/{course_id}")
def update_course(course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course_update.code and course_update.code != course.code:
        if db.query(Course).filter(Course.code == course_update.code).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")

    if course_update.title is not None:
        course.title = course_update.title
    if course_update.code is not None:
        course.code = course_update.code
    if course_update.capacity is not None:
        course.capacity = course_update.capacity
    if course_update.is_active is not None:
        course.is_active = course_update.is_active

    db.commit()
    db.refresh(course)
    return success_response(data=course.to_dict(), message="Course updated")


@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.is_active = False
    db.commit()
    return success_response(data=None, message="Course deleted")


@router.patch("/{course_id}/activate")
def activate_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.is_active = True
    db.commit()
    db.refresh(course)
    return success_response(data=course.to_dict(), message="Course activated")


@router.patch("/{course_id}/deactivate")
def deactivate_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.is_active = False
    db.commit()
    db.refresh(course)
    return success_response(data=course.to_dict(), message="Course deactivated")
