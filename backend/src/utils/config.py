"""
Environment variables configuration for the game ratings service.
"""

# mypy: ignore-errors
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    CURRENT_ENV: str
    HOST: str
    PORT: int
    API_TOKEN: SecretStr
    FRONTEND_BUILD_DIR: str = "frontend/dist"  # Default to dist for production
    FRONTEND_URL: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_ROOT_PASSWORD: SecretStr
    MYSQL_DB_NAME: str
    PROTOCOL: str = "https"  # Default to HTTPS for security
    LOG_LEVEL: str = (
        "INFO"  # Default to INFO for development change to ERROR for production
    )
    AUTH_EMAIL_HOST: str
    AUTH_EMAIL_PORT: int
    AUTH_EMAIL_HOST_USER: str
    AUTH_EMAIL_HOST_PASSWORD: SecretStr
    AUTH_EMAIL_USE_TLS: bool = True
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    @property
    def DB_URL(self) -> str:
        """Get formatted database URL."""
        password = self.MYSQL_ROOT_PASSWORD.get_secret_value()
        return f"mysql+pymysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB_NAME}"

    @property
    def API_TOKEN_VALUE(self) -> str:
        """Get API token value."""
        return self.API_TOKEN.get_secret_value()

    @property
    def AUTH_EMAIL_HOST_PASSWORD_VALUE(self) -> str:
        """Get email host password value."""
        return self.AUTH_EMAIL_HOST_PASSWORD.get_secret_value()

    @property
    def SECRET_KEY_VALUE(self) -> str:
        """Get secret key value."""
        return self.SECRET_KEY.get_secret_value()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


# Create a singleton instance
app_settings = Settings()
