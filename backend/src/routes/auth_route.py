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

    This endpoint creates a new user account with the provided information and sends
    a verification email to the user's email address. The user will need to verify
    their email before they can log in.

    Authentication:
        - No authentication required

    Request Body:
        - email: String (required) - Valid email address
        - username: String (required) - Username between 3-50 characters
        - password: String (required) - Password at least 4 characters long
        - full_name: String (optional) - User's full name

    Returns:
        - 201 Created: Object containing:
            - message: "User registered successfully"
            - user_id: Integer - ID of the newly created user
            - verification_email_sent: Boolean - Whether the verification email was sent
            - verification_required: Boolean - Whether email verification is required
        - 400 Bad Request: If email is already registered or username is taken
        - 422 Unprocessable Entity: If the request body is invalid

    Example Request:
        ```json
        {
            "email": "user@example.com",
            "username": "johndoe",
            "password": "securepassword123",
            "full_name": "John Doe"
        }
        ```

    Example Response:
        ```json
        {
            "message": "User registered successfully",
            "user_id": 1,
            "verification_email_sent": true,
            "verification_required": true
        }
        ```

    Notes for Frontend Developers:
        - After registration, display a message to the user to check their email
        - The user will not be able to log in until they verify their email
        - You may want to provide a way for users to request a new verification email
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


@router.post("/send-verification-email", response_model=Dict[str, Any])
async def send_verification_email(
    verification_data: EmailVerificationRequest, db: Session = Depends(get_db)
):
    """
    Send or resend a verification email to the specified email address.

    This endpoint allows users to request a verification email in case they did not
    receive the initial email or if the verification link expired.

    Authentication:
        - No authentication required

    Request Body:
        - email: String (required) - Email address to send verification to

    Returns:
        - 200 OK: Object containing:
            - message: String - Status message
            - email_sent: Boolean - Whether the email was sent successfully
        - 404 Not Found: If no user with the provided email exists
        - 422 Unprocessable Entity: If the request body is invalid

    Example Request:
        ```json
        {
            "email": "user@example.com"
        }
        ```

    Example Response:
        ```json
        {
            "message": "Verification email sent successfully",
            "email_sent": true
        }
        ```

    Notes for Frontend Developers:
        - This endpoint is useful for implementing a "Resend verification email" feature
        - Display appropriate feedback to the user about checking their inbox
    """
    # Check if user exists
    user = (
        db.query(models.User)
        .filter(models.User.email == verification_data.email)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Generate verification token
    verification_token = auth_service.create_verification_token(verification_data.email)

    # Send verification email
    email_sent = email_service.send_verification_email(
        verification_data.email, verification_token
    )

    return {
        "message": (
            "Verification email sent successfully"
            if email_sent
            else "Failed to send verification email"
        ),
        "email_sent": email_sent,
    }


@router.post("/verify-email", response_model=Dict[str, Any])
async def verify_email(verify_data: VerifyTokenRequest, db: Session = Depends(get_db)):
    """
    Verify a user's email address using the verification token.

    This endpoint is used to confirm a user's email address by validating the token
    that was sent to their email during registration or when requesting a verification email.
    Once verified, the user's account will be activated.

    Authentication:
        - No authentication required

    Request Body:
        - token: String (required) - Verification token received via email

    Returns:
        - 200 OK: Object containing:
            - message: String - Success message
            - verified: Boolean - Whether verification was successful
        - 400 Bad Request: If the token is invalid or expired
        - 422 Unprocessable Entity: If the request body is invalid

    Example Request:
        ```json
        {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        ```

    Example Response:
        ```json
        {
            "message": "Email verified successfully",
            "verified": true
        }
        ```

    Notes for Frontend Developers:
        - After successful verification, guide the user to the login page
        - Consider displaying a message explaining that their account is now active
    """
    try:
        # Verify token and get email
        token_result = auth_service.verify_token(verify_data.token)

        # Handle the case where verify_token returns a tuple (success, email)
        email = None
        if isinstance(token_result, tuple) and len(token_result) == 2:
            success, email = token_result
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token",
                )
        else:
            # If it's not a tuple, assume it's just the email string
            email = token_result

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        # Find user by email
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Activate user account
        user.is_active = True
        db.commit()

        return {"message": "Email verified successfully", "verified": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}",
        )


@router.post("/login", response_model=Dict[str, Any])
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Log in a user with email and password.

    This endpoint authenticates a user with their email and password, and if successful,
    returns an access token and sets a refresh token cookie. The access token should be
    used for authenticated API requests, while the refresh token is used to obtain new
    access tokens when they expire.

    Authentication:
        - No authentication required

    Request Body:
        - email: String (required) - User's email address
        - password: String (required) - User's password
        - remember_me: Boolean (optional) - Whether to extend token validity periods

    Returns:
        - 200 OK: Object containing:
            - message: String - Success message
            - access_token: String - JWT access token for API authorization
            - token_type: String - Type of token (always "bearer")
            - user: Object - User information including:
                - id: Integer - User ID
                - email: String - User's email
                - username: String - User's username
                - full_name: String - User's full name (if provided)
        - 400 Bad Request: If the email is not verified
        - 401 Unauthorized: If the email or password is incorrect
        - 422 Unprocessable Entity: If the request body is invalid

    Cookies:
        - refresh_token: HTTP-only secure cookie containing the refresh token

    Example Request:
        ```json
        {
            "email": "user@example.com",
            "password": "securepassword123",
            "remember_me": true
        }
        ```

    Example Response:
        ```json
        {
            "message": "Login successful",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe"
            }
        }
        ```

    Notes for Frontend Developers:
        - Store the access token securely (preferably in memory, not localStorage)
        - Include the access token in API requests using the Authorization header:
          "Authorization: Bearer {access_token}"
        - The refresh token is automatically handled via cookies
        - Implement a token refresh mechanism when access tokens expire
    """
    # Find user by email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user's email is verified
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified. Please verify your email before logging in.",
        )

    # Determine token expiration based on remember_me flag
    access_token_expires = (
        auth_service.ACCESS_TOKEN_EXPIRE_MINUTES_EXTENDED
        if login_data.remember_me
        else auth_service.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = (
        auth_service.REFRESH_TOKEN_EXPIRE_DAYS_EXTENDED
        if login_data.remember_me
        else auth_service.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_minutes=access_token_expires
    )

    # Create refresh token
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.email}, expires_days=refresh_token_expires
    )

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Set to False in development if not using HTTPS
        samesite="lax",  # Adjust based on your security requirements
        max_age=refresh_token_expires * 24 * 60 * 60,  # Convert days to seconds
    )

    # Return response with access token and user info
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
        },
    }


@router.post("/refresh-token", response_model=Dict[str, Any])
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db),
):
    """
    Refresh the access token using a refresh token.

    This endpoint allows clients to obtain a new access token when the current one expires,
    without requiring the user to log in again. It uses the refresh token stored in an
    HTTP-only cookie.

    Authentication:
        - Requires a valid refresh token in cookies

    Parameters:
        - None (uses the refresh_token cookie)

    Returns:
        - 200 OK: Object containing:
            - access_token: String - New JWT access token
            - token_type: String - Token type (always "bearer")
        - 401 Unauthorized: If the refresh token is missing, invalid, or expired

    Cookies:
        - A new refresh token is set if the current one is valid

    Example Response:
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        ```

    Notes for Frontend Developers:
        - Call this endpoint when an API request fails with a 401 status code
        - The endpoint requires no body or headers as it uses HTTP cookies
        - After getting a new access token, retry the failed request
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        # Verify refresh token and get email
        email = auth_service.verify_token(refresh_token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Verify user exists and is active
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new access token
        access_token = auth_service.create_access_token(data={"sub": email})

        # Create new refresh token (rotation for security)
        new_refresh_token = auth_service.create_refresh_token(data={"sub": email})

        # Set new refresh token as HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,  # Set to False in development if not using HTTPS
            samesite="lax",  # Adjust based on your security requirements
            max_age=auth_service.REFRESH_TOKEN_EXPIRE_DAYS
            * 24
            * 60
            * 60,  # Convert days to seconds
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate refresh token: {str(e)}",
        )


@router.post("/logout", response_model=Dict[str, str])
async def logout(response: Response):
    """
    Log out a user by clearing their refresh token cookie.

    This endpoint invalidates the user's session by clearing the refresh token cookie.
    The frontend should also discard the access token.

    Authentication:
        - No authentication required, but typically called with a valid session

    Parameters:
        - None

    Returns:
        - 200 OK: Object containing:
            - message: String - Confirmation of logout

    Cookies:
        - Clears the refresh_token cookie

    Example Response:
        ```json
        {
            "message": "Logged out successfully"
        }
        ```

    Notes for Frontend Developers:
        - Send credentials = include the access token in the Authorization header
        - After calling this endpoint, also clear the access token from your application state
        - Redirect the user to the login page or home page after successful logout
    """
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}


@router.post("/forgot-password", response_model=Dict[str, Any])
async def forgot_password(
    email_data: EmailVerificationRequest, db: Session = Depends(get_db)
):
    """
    Request a password reset email.

    This endpoint sends a password reset email to the user with a token that can be used
    to reset their password.

    Authentication:
        - No authentication required

    Request Body:
        - email: String (required) - Email address of the account

    Returns:
        - 200 OK: Object containing:
            - message: String - Status message
            - email_sent: Boolean - Whether the email was sent successfully
        - 404 Not Found: If no user with the provided email exists
        - 422 Unprocessable Entity: If the request body is invalid

    Example Request:
        ```json
        {
            "email": "user@example.com"
        }
        ```

    Example Response:
        ```json
        {
            "message": "Password reset email sent",
            "email_sent": true
        }
        ```

    Notes for Frontend Developers:
        - Display a message to the user to check their email
        - Do not reveal whether the email exists in the system for security reasons
          (the API will still return 200 even if the email doesn't exist)
    """
    # Check if user exists (but don't reveal this information in the response)
    user = db.query(models.User).filter(models.User.email == email_data.email).first()

    # If user doesn't exist, still return success but don't send email
    # This prevents email enumeration attacks
    if not user:
        return {
            "message": "If a user with this email exists, a password reset email has been sent",
            "email_sent": False,
        }

    # Generate password reset token
    reset_token = auth_service.create_password_reset_token(email_data.email)

    # Send password reset email
    email_sent = email_service.send_password_reset_email(email_data.email, reset_token)

    return {
        "message": "Password reset email sent",
        "email_sent": email_sent,
    }


class ResetPasswordRequest(BaseModel):
    """Password reset request model with token and new password."""

    token: str
    new_password: str = Field(..., min_length=4)

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "newSecurePassword123",
            }
        }


@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(
    reset_data: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """
    Reset a user's password using a reset token.

    This endpoint allows users to set a new password after receiving a password reset token
    via email.

    Authentication:
        - No authentication required

    Request Body:
        - token: String (required) - Password reset token received via email
        - new_password: String (required) - New password (minimum 4 characters)

    Returns:
        - 200 OK: Object containing:
            - message: String - Success message
            - password_reset: Boolean - Whether the password was reset successfully
        - 400 Bad Request: If the token is invalid or expired
        - 422 Unprocessable Entity: If the request body is invalid

    Example Request:
        ```json
        {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "new_password": "newSecurePassword123"
        }
        ```

    Example Response:
        ```json
        {
            "message": "Password reset successful",
            "password_reset": true
        }
        ```

    Notes for Frontend Developers:
        - After a successful password reset, redirect the user to the login page
        - Provide clear feedback about password requirements
    """
    try:
        # Verify token and get email
        email = auth_service.verify_token(reset_data.token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        # Find user by email
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Hash new password
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(reset_data.new_password)

        # Update user's password
        user.hashed_password = hashed_password
        db.commit()

        return {"message": "Password reset successful", "password_reset": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset failed: {str(e)}",
        )


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


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.

    This endpoint returns information about the current user based on their
    authentication token. It's useful for getting user details after login
    or refreshing user information.

    Authentication:
        - Requires Bearer token in the Authorization header
          OR a valid session token in cookies
        - Example: Authorization: Bearer <your_token>

    Returns:
        - 200 OK: User object with details including:
            - id: Integer - User ID
            - email: String - User's email address
            - username: String - User's username
            - full_name: String - User's full name (if provided)
            - is_active: Boolean - Whether the user is active
            - created_at: String - ISO timestamp of when the user was created
        - 401 Unauthorized: If no valid authentication is provided

    Example Response:
        ```json
        {
            "id": 1,
            "email": "user@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "is_active": true,
            "created_at": "2023-07-01T10:00:00Z"
        }
        ```

    Notes for Frontend Developers:
        - Use this endpoint to check if the user is still authenticated
        - Call this when your application loads to restore user state
        - You can use this to get updated user information at any time
        - If this endpoint returns 401, redirect to the login page
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat(),
    }
