import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VeriBorder — AI Fake Identity & Document Screening System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Neon PostgreSQL connection string (or fallback to SQLite)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    SECRET_KEY: str = "veriborder_sih26187_border_security_secret_key_2026"
    DEBUG: bool = True
    
    # Directories for static uploads, ELA heatmaps, and preset samples
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "static", "uploads")
    ELA_DIR: str = os.path.join(BASE_DIR, "static", "ela")
    SAMPLE_DIR: str = os.path.join(BASE_DIR, "static", "samples")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
for folder in [settings.UPLOAD_DIR, settings.ELA_DIR, settings.SAMPLE_DIR]:
    os.makedirs(folder, exist_ok=True)
