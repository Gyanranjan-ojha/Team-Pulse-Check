"""
Authentication service for managing user authentication and verification.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple

from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from ..db import models
from ..utils.logger import app_logger
from ..utils.config import app_settings


class AuthService:
    """
    Service for handling authentication-related functionality.
    """

    def __init__(self):
        """Initialize the authentication service."""
        self.secret_key = app_settings.SECRET_KEY_VALUE
        self.algorithm = app_settings.ALGORITHM
        self.verification_token_expire_minutes = (
            app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
        )
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_expire_minutes = 60  # 1 hour
        self.session_expire_days = 7  # 7 days for session

    def create_verification_token(self, email: str) -> str:
        """
        Create a verification token for email verification.

        Args:
            email: The email address to verify

        Returns:
            str: JWT token that can be used for verification
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.verification_token_expire_minutes
        )
        to_encode = {"sub": email, "exp": expire, "type": "email_verification"}

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(
        self, token: str, token_type: str = "email_verification"
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify a token and return the email if valid.

        Args:
            token: JWT token to verify
            token_type: Type of token to verify (default: "email_verification")

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, email if valid or None)
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            exp = payload.get("exp")
            token_type_from_payload = payload.get("type")

            if not email or not exp:
                return False, None

            # Check if token is of correct type
            if token_type_from_payload != token_type:
                return False, None

            # Token is valid, return the email
            return True, email

        except JWTError as e:
            app_logger.error(f"JWT verification error: {str(e)}")
            return False, None

    def process_email_verification(self, db: Session, token: str) -> Tuple[bool, str]:
        """
        Process email verification by validating the token and updating the user's status.

        Args:
            db: Database session
            token: Verification token

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Verify the token
        is_valid, email = self.verify_token(token)

        if not is_valid or not email:
            return False, "Invalid or expired verification token"

        # Find the user by email
        user = db.query(models.User).filter(models.User.email == email).first()

        if not user:
            return False, "User not found"

        # Check if already verified
        if user.is_active:
            return True, "Email already verified"

        # Update user status
        user.is_active = True
        db.commit()

        return True, "Email verification successful"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: The plaintext password to verify
            hashed_password: The hashed password to check against

        Returns:
            bool: True if the password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plaintext password to hash

        Returns:
            str: The hashed password
        """
        return self.pwd_context.hash(password)

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[models.User]:
        """
        Authenticate a user by verifying their email and password.

        Args:
            db: Database session
            email: User's email
            password: User's password

        Returns:
            Optional[models.User]: The user if authentication is successful, None otherwise
        """
        user = db.query(models.User).filter(models.User.email == email).first()

        if not user or not self.verify_password(password, user.hashed_password):
            return None

        # Check if user is active (email verified)
        if not user.is_active:
            return None

        return user

    def create_user_session(
        self,
        db: Session,
        user: models.User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> models.UserSession:
        """
        Create a new session for a user.

        Args:
            db: Database session
            user: The user to create a session for
            ip_address: IP address of the client
            user_agent: User agent of the client

        Returns:
            models.UserSession: The created session
        """
        # Generate a random token for the session
        token = secrets.token_urlsafe(32)

        # Set expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self.session_expire_days
        )

        # Create a new session
        session = models.UserSession(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
        )

        # Update last login time for the user
        user.last_login = datetime.now(timezone.utc)

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    def validate_session(self, db: Session, token: str) -> Optional[models.User]:
        """
        Validate a session token and return the associated user.

        Args:
            db: Database session
            token: Session token to validate

        Returns:
            Optional[models.User]: The user if the session is valid, None otherwise
        """
        session = (
            db.query(models.UserSession)
            .filter(
                models.UserSession.token == token,
                models.UserSession.is_active == True,
                models.UserSession.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

        if not session:
            return None

        # Update last active time
        session.last_active_at = datetime.now(timezone.utc)
        db.commit()

        # Return the user associated with this session
        return session.user

    def terminate_session(self, db: Session, token: str) -> bool:
        """
        Terminate a user session (logout).

        Args:
            db: Database session
            token: Session token to terminate

        Returns:
            bool: True if the session was terminated, False otherwise
        """
        session = (
            db.query(models.UserSession)
            .filter(
                models.UserSession.token == token, models.UserSession.is_active == True
            )
            .first()
        )

        if not session:
            return False

        session.is_active = False
        db.commit()

        return True


# Create a singleton instance
auth_service = AuthService()
