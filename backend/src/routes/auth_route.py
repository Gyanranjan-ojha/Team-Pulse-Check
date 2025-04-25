"""
Authentication routes including login, registration, and email verification.
"""

import os
from typing import Dict, Any, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    Request,
    Response,
    Cookie,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from ..db.database import get_db
from ..db import models
from ..services.email_service import email_service
from ..services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic models for request validation
class UserCreate(BaseModel):
    """User registration model."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)
    full_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123",
                "full_name": "John Doe",
            }
        }


class EmailVerificationRequest(BaseModel):
    """Email verification request model."""

    email: EmailStr

    class Config:
        json_schema_extra = {"example": {"email": "user@example.com"}}


class VerifyTokenRequest(BaseModel):
    """Token verification request model."""

    token: str

    class Config:
        json_schema_extra = {
            "example": {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr
    password: str
    remember_me: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "remember_me": True,
            }
        }


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any]
)
async def register_user(
    user_data: UserCreate, request: Request, db: Session = Depends(get_db)
):
    """
    Register a new user and send verification email.
    """
    # Check if user with this email already exists
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username is taken
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create user (you would typically hash the password here)
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed_password = pwd_context.hash(user_data.password)

    # Create new user with is_active=False until email is verified
    new_user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=False,  # User is inactive until email verification
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate verification token
    verification_token = auth_service.create_verification_token(user_data.email)

    # Send verification email
    email_sent = email_service.send_verification_email(
        user_data.email, verification_token
    )

    # Return response
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "verification_email_sent": email_sent,
        "verification_required": True,
    }


@router.post("/send-verification-email", status_code=status.HTTP_200_OK)
async def send_verification_email(
    request_data: EmailVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Send or resend a verification email to the user.
    """
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == request_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if already verified
    if user.is_active:
        return {"message": "Email already verified"}

    # Generate verification token
    verification_token = auth_service.create_verification_token(request_data.email)

    # Send verification email
    email_sent = email_service.send_verification_email(
        request_data.email, verification_token
    )

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )

    return {"message": "Verification email sent successfully"}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(token_data: VerifyTokenRequest, db: Session = Depends(get_db)):
    """
    Verify email using the token sent to the user's email.
    """
    success, message = auth_service.process_email_verification(db, token_data.token)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"message": message}


@router.get("/verify-email/{token}", status_code=status.HTTP_200_OK)
async def verify_email_get(token: str, db: Session = Depends(get_db)):
    """
    Alternative GET endpoint for email verification (for direct link in emails).
    """
    success, message = auth_service.process_email_verification(db, token)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"message": message}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and create a session.

    Args:
        login_data: Login credentials
        response: FastAPI response object for setting cookies
        request: FastAPI request object for getting client info
        db: Database session

    Returns:
        Dict with user information and session token
    """
    # Authenticate user
    user = auth_service.authenticate_user(
        db=db, email=login_data.email, password=login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Create session
    session = auth_service.create_user_session(
        db=db, user=user, ip_address=ip_address, user_agent=user_agent
    )

    # Set session cookie
    max_age = (
        7 * 24 * 60 * 60 if login_data.remember_me else None
    )  # 7 days if remember_me is True
    secure = request.url.scheme == "https"

    response.set_cookie(
        key="session_token",
        value=session.token,
        httponly=True,
        max_age=max_age,
        expires=max_age,
        secure=secure,
        samesite="lax",
    )

    # Return user info
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_superuser": user.is_superuser,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response, session_token: str = Cookie(None), db: Session = Depends(get_db)
):
    """
    Logout the user by terminating their session.

    Args:
        response: FastAPI response object for clearing cookies
        session_token: Session token from cookie
        db: Database session

    Returns:
        Dict with logout message
    """
    if not session_token:
        return {"message": "No active session"}

    # Terminate the session
    success = auth_service.terminate_session(db=db, token=session_token)

    # Clear the session cookie
    response.delete_cookie(
        key="session_token", httponly=True, secure=True, samesite="lax"
    )

    return {"message": "Logout successful"}


# Dependency to get the current user from the session
async def get_current_user(
    session_token: str = Cookie(None), db: Session = Depends(get_db)
) -> Optional[models.User]:
    """
    Get the current authenticated user from the session token.

    Args:
        session_token: Session token from cookie
        db: Database session

    Returns:
        Optional[models.User]: The authenticated user or None
    """
    if not session_token:
        return None

    return auth_service.validate_session(db=db, token=session_token)


# Protected route example
@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """
    Get information about the current authenticated user.

    Args:
        current_user: Current authenticated user

    Returns:
        Dict with user information
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_superuser": current_user.is_superuser,
    }
