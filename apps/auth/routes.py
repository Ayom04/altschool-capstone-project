from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from apps.config.database import get_db
from apps.config.config import get_settings
from apps.users.schemas import UserLogin
from apps.users.services import authenticate_user
from apps.common.security import create_access_token
from apps.common.responses import success_response

settings = get_settings()
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return success_response(
        data={"access_token": access_token, "token_type": "bearer"},
        message="Login successful"
    )
