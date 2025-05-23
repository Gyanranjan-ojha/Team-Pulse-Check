"""
Email service for sending verification emails and other email notifications.
"""

import os
import smtplib
from typing import Dict, Optional, Any

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..utils.config import app_settings
from ..utils.logger import app_logger


class EmailService:
    """
    Service for sending emails using SMTP.
    Uses environment variables for configuration.
    """

    def __init__(self):
        """Initialize the email service with configuration from environment variables."""
        self.email_host = app_settings.AUTH_EMAIL_HOST
        self.email_port = app_settings.AUTH_EMAIL_PORT
        self.email_user = app_settings.AUTH_EMAIL_HOST_USER
        self.email_password = app_settings.AUTH_EMAIL_HOST_PASSWORD_VALUE
        self.use_tls = app_settings.AUTH_EMAIL_USE_TLS
        self.sender = app_settings.AUTH_EMAIL_HOST_USER
        self.frontend_url = app_settings.FRONTEND_URL

        if not self.email_user or not self.email_password:
            app_logger.warning(
                "Email credentials not properly configured. " "Emails will not be sent."
            )

    def _create_message(
        self, recipient: str, subject: str, body: str, html_body: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Create an email message.

        Args:
            recipient: Email address of the recipient
            subject: Email subject
            body: Plain text email body
            html_body: HTML version of the email body (optional)

        Returns:
            MIMEMultipart: The constructed email message
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = recipient

        # Attach plain text version
        text_part = MIMEText(body, "plain")
        message.attach(text_part)

        # Attach HTML version if provided
        if html_body:
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

        return message

    def send_email(
        self, recipient: str, subject: str, body: str, html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email.

        Args:
            recipient: Email address of the recipient
            subject: Email subject
            body: Plain text email body
            html_body: HTML version of the email body (optional)

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.email_user or not self.email_password:
            app_logger.error("Email service not properly configured")
            return False

        message = self._create_message(recipient, subject, body, html_body)

        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.sender, recipient, message.as_string())

            app_logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            app_logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_verification_email(self, email: str, verification_token: str) -> bool:
        """
        Send a verification email to a user.

        Args:
            email: User's email address
            verification_token: Token for email verification

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        verification_url = (
            f"{self.frontend_url}/verify-email?token={verification_token}"
        )

        subject = "Verify your email address"

        body = f"""
        Hello,

        Please verify your email address by clicking on the link below:

        {verification_url}

        If you did not sign up for this account, you can ignore this email.

        Thanks,
        The PulseCheck Team
        """

        html_body = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Hello,</p>
            <p>Please verify your email address by clicking on the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>If you did not sign up for this account, you can ignore this email.</p>
            <p>Thanks,<br>The PulseCheck Team</p>
        </body>
        </html>
        """

        return self.send_email(email, subject, body, html_body)

    def send_password_reset_email(self, recipient: str, token: str) -> bool:
        """
        Send a password reset link to a user.

        Args:
            recipient: Email address of the recipient
            token: Password reset token

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        reset_url = f"{self.frontend_url}/reset-password?token={token}"

        subject = "Reset Your Password - Team Pulse Check"

        body_html = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>We received a request to reset your password. Click the link below to create a new password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{reset_url}</p>
                <p>This link will expire in 30 minutes for security reasons.</p>
                <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
                <p>Thanks,<br>The Team Pulse Check Team</p>
            </body>
        </html>
        """

        return self.send_email(recipient, subject, body_html)


# Create a singleton instance
email_service = EmailService()
