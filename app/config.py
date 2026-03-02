from pathlib import Path
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
_ENV_FILE_STR = str(_ENV_FILE) if _ENV_FILE.exists() else None


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

    # Default OpenMRS user ID to attribute new records to when not provided
    default_creator_id: int = 1

    # Vital signs concept IDs (comma-separated)
    vital_signs_concept_ids: str = ""
    vital_signs_body_position_concept_id: str = ""

    # Physical examination settings
    consultation_encounter_type_id: int = 1
    consultation_encounter_role_id: int = 1
    physical_exam_concept_ids: str = "35"

    # Chief complaint concept IDs
    cc_group_concept_id: int = 57422
    cc_coded_concept_id: int = 57385
    cc_text_concept_id: int = 30201
    cc_duration_concept_id: int = 11266
    cc_duration_unit_concept_id: int = 57386
    cc_hpi_concept_id: int = 16086

    # Chief complaint form_namespace_and_path values
    cc_form_group: str = "Bahmni^History and Examination.1/25-0"
    cc_form_complaint: str = "Bahmni^History and Examination.1/25-0/26-0"
    cc_form_duration: str = "Bahmni^History and Examination.1/25-0/28-0"
    cc_form_duration_unit: str = "Bahmni^History and Examination.1/25-0/29-0"
    cc_form_hpi: str = "Bahmni^History and Examination.1/7-0"

    # OpenMRS REST configuration for post-processing (e.g., search index updates)
    openmrs_base_url: str = "http://localhost:8080/openmrs"
    openmrs_rest_username: str | None = None
    openmrs_rest_password: str | None = None
    openmrs_rest_timeout_seconds: float = 10.0
    openmrs_rest_verify_ssl: bool = True

    class Config:
        env_file = _ENV_FILE_STR
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


# Vital signs concept ID helpers
def get_vital_signs_concept_ids() -> list[int]:
    """Parse comma-separated vital sign concept IDs from environment variable"""
    ids = []
    for part in settings.vital_signs_concept_ids.split(","):
        part = part.strip()
        if part:
            try:
                ids.append(int(part))
            except ValueError:
                pass
    if settings.vital_signs_body_position_concept_id.strip():
        try:
            body_pos_id = int(settings.vital_signs_body_position_concept_id.strip())
            if body_pos_id not in ids:
                ids.append(body_pos_id)
        except ValueError:
            pass
    return ids


# Physical exam concept ID helpers
def get_physical_exam_concept_ids() -> list[int]:
    """Parse comma-separated physical exam concept IDs from environment variable"""
    ids = []
    for part in settings.physical_exam_concept_ids.split(","):
        part = part.strip()
        if part:
            try:
                ids.append(int(part))
            except ValueError:
                pass
    return ids


# Database URL
def get_database_url() -> str:
    """Generate database URL for SQLAlchemy"""
    return f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
