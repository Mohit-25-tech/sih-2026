import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api.routes import router as api_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("veriborder.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Based Fake Identity & Document Screening System — SIH 2026 (SIH26187)"
)

# CORS Middleware Setup
origins = settings.ALLOWED_ORIGINS.split(",") if hasattr(settings, "ALLOWED_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow dashboard local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files Directory
static_dir = os.path.join(settings.BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API Router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing VeriBorder Backend Database & Services...")
    init_db()
    logger.info("VeriBorder Engine online and ready.")

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "system": "VeriBorder — AI Document Screening System",
        "event": "Smart India Hackathon 2026",
        "team": "Zenith",
        "problem_id": "SIH26187",
        "docs_url": "/docs"
    }
