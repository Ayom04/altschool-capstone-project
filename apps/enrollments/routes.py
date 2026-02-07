from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from apps.config.database import get_db
from apps.enrollments.models import Enrollment
from apps.enrollments.schemas import EnrollmentCreate, EnrollmentResponse, EnrollmentWithDetails
from apps.courses.models import Course
from apps.users.models import User, UserRole
from apps.common.security import get_current_active_user, require_admin
from apps.common.responses import success_response

router = APIRouter(prefix="/api/v1/enrollments", tags=["enrollments"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=None)
def enroll_in_course(enrollment_data: EnrollmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only students can enroll")

    course = db.query(Course).filter(
        Course.id == enrollment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if not course.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot enroll in inactive course")

    if db.query(Enrollment).filter(Enrollment.user_id == current_user.id, Enrollment.course_id == enrollment_data.course_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled")

    if course.is_full:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Course is at full capacity")

    new_enrollment = Enrollment(
        user_id=current_user.id, course_id=enrollment_data.course_id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    # Eagerly load relationships
    enrollment_with_relations = db.query(Enrollment).options(
        joinedload(Enrollment.user),
        joinedload(Enrollment.course)
    ).filter(Enrollment.id == new_enrollment.id).first()

    return success_response(data=enrollment_with_relations.to_dict(), message="Enrolled successfully")


@router.delete("/{enrollment_id}")
def deregister_from_course(enrollment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    if enrollment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Cannot deregister another student")

    db.delete(enrollment)
    db.commit()
    return success_response(data=None, message="Deregistered")


@router.delete("/courses/{course_id}/deregister")
def deregister_by_course_id(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id, Enrollment.course_id == course_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not enrolled")
    db.delete(enrollment)
    db.commit()
    return success_response(data=None, message="Deregistered")


@router.get("/my-enrollments", response_model=None)
def get_my_enrollments(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    enrollments = db.query(Enrollment).options(
        joinedload(Enrollment.user),
        joinedload(Enrollment.course)
    ).filter(Enrollment.user_id == current_user.id).all()
    return success_response(data=[e.to_dict() for e in enrollments], message="My enrollments retrieved")


@router.get("", response_model=None)
def get_all_enrollments(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    course_id: int = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """
    Get all enrollments with optional filtering and pagination (Admin only).
    
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - user_id: Filter by user ID
    - course_id: Filter by course ID
    """
    # Limit max page size
    limit = min(limit, 1000)
    
    query = db.query(Enrollment).options(
        joinedload(Enrollment.user),
        joinedload(Enrollment.course)
    )
    
    # Apply filters
    if user_id:
        query = query.filter(Enrollment.user_id == user_id)
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    enrollments = query.offset(skip).limit(limit).all()
    
    return success_response(
        data={
            "items": [e.to_dict() for e in enrollments],
            "total": total,
            "skip": skip,
            "limit": limit
        },
        message="All enrollments retrieved"
    )


@router.get("/courses/{course_id}", response_model=None)
def get_enrollments_for_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    enrollments = db.query(Enrollment).options(
        joinedload(Enrollment.user),
        joinedload(Enrollment.course)
    ).filter(Enrollment.course_id == course_id).all()
    return success_response(data=[e.to_dict() for e in enrollments], message="Course enrollments retrieved")


@router.delete("/admin/{enrollment_id}")
def admin_remove_student(enrollment_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
    return success_response(data=None, message="Student removed")
