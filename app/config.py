from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "openmrs"
    db_user: str = "root"
    db_password: str = ""

    # API settings
    api_keys: str = ""  # Comma-separated list of valid API keys
    port: int = 1221
    host: str = "0.0.0.0"

    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Debug mode
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Create settings instance
settings = Settings()


# Parse API keys from environment
def get_valid_api_keys() -> list[str]:
    """Parse comma-separated API keys from environment variable"""
    if not settings.api_keys:
        return []
    return [key.strip() for key in settings.api_keys.split(",") if key.strip()]


# Database URL
def get_database_url() -> str:
    """Generate database URL for SQLAlchemy"""
    return f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
