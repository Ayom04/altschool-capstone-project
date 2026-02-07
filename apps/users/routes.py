from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from apps.config.database import get_db
from apps.users.models import User
from apps.users.schemas import UserCreate, UserUpdate
from apps.users.services import get_user_by_email
from apps.common.security import hash_password, get_current_active_user, require_admin
from apps.common.responses import success_response

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return success_response(data=new_user.to_dict(), message="User registered successfully")


@router.get("/me", response_model=None)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return success_response(data=current_user.to_dict(), message="Profile retrieved successfully")


@router.get("/me/with-enrollments", response_model=None)
def get_my_profile_with_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get current user profile with enrolled courses"""
    user_with_enrollments = db.query(User).options(
        joinedload(User.enrollments)
    ).filter(User.id == current_user.id).first()

    return success_response(data=user_with_enrollments.to_dict(include_enrollments=True), message="Profile with courses retrieved successfully")


@router.put("/me")
def update_my_profile(user_update: UserUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    db.commit()
    db.refresh(current_user)
    return success_response(data=current_user.to_dict(), message="Profile updated successfully")


@router.get("", response_model=None)
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    role: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """
    Get all users with optional filtering and pagination (Admin only).
    
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - search: Search users by name or email (case-insensitive)
    - role: Filter by role (student/admin)
    - is_active: Filter by active status (true/false)
    """
    # Limit max page size
    limit = min(limit, 1000)
    
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_term)) | (User.email.ilike(search_term))
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return success_response(
        data={
            "items": [u.to_dict() for u in users],
            "total": total,
            "skip": skip,
            "limit": limit
        },
        message="Users retrieved successfully"
    )



@router.get("/{user_id}", response_model=None)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return success_response(data=user.to_dict(), message="User retrieved successfully")


@router.get("/{user_id}/with-enrollments", response_model=None)
def get_user_with_enrollments(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Get user with enrolled courses"""
    user_with_enrollments = db.query(User).options(
        joinedload(User.enrollments)
    ).filter(User.id == user_id).first()

    if not user_with_enrollments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return success_response(data=user_with_enrollments.to_dict(include_enrollments=True), message="User with courses retrieved successfully")
