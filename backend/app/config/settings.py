import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    Uses pydantic-settings to validate configuration types automatically.
    """
    # MongoDB settings
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "papermind_db"
    
    # JWT security settings
    JWT_SECRET: str = "papermind_super_secret_jwt_signing_key_secure_2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440
    
    # Gemini API setting
    GEMINI_API_KEY: str = ""

    # Uploads path setting
    UPLOAD_DIR: str = "uploads"

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings to be imported by other files
settings = Settings()
