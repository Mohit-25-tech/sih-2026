import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger("veriborder.database")

Base = declarative_base()

def get_database_engine():
    db_url = settings.DATABASE_URL.strip() if settings.DATABASE_URL else ""
    
    if db_url:
        # Handle postgresql:// schema adjustment if needed
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        try:
            logger.info(f"Connecting to Neon PostgreSQL database...")
            engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={"sslmode": "require"} if "neon.tech" in db_url else {}
            )
            # Test connection
            with engine.connect() as conn:
                logger.info("Successfully connected to Neon PostgreSQL!")
            return engine
        except Exception as e:
            logger.warning(f"Failed to connect to Neon PostgreSQL ({e}). Falling back to local SQLite database.")
    
    # Fallback SQLite Database
    sqlite_url = f"sqlite:///{os.path.join(settings.BASE_DIR, 'veriborder.db')}"
    logger.info(f"Using SQLite database: {sqlite_url}")
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app import models  # Ensure models are imported
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
