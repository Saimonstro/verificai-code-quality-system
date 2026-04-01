"""
FastAPI application entry point for VerificAI Code Quality System - Demo Mode
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables, db_manager
from app.core.logging import setup_logging
from app.core.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    ErrorHandlerMiddleware,
    RateLimitMiddleware
)
from app.api.v1 import auth, users, prompts, analysis, upload, file_paths, general_analysis, simple_analysis, code_entries
import uvicorn

# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered code quality analysis system for QA teams",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS - allows all origins in demo mode, can be restricted via env var
cors_origins = settings.BACKEND_CORS_ORIGINS + ["*"] if settings.ENVIRONMENT == "production" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware stack
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(file_paths.router, prefix=settings.API_V1_STR + "/file-paths", tags=["file_paths"])
app.include_router(code_entries.router, prefix=settings.API_V1_STR, tags=["code_entries"])
app.include_router(prompts.router, prefix=settings.API_V1_STR + "/prompts", tags=["prompts"])
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["analysis"])
app.include_router(upload.router, prefix=settings.API_V1_STR, tags=["upload"])
app.include_router(general_analysis.router, prefix=settings.API_V1_STR + "/general-analysis", tags=["general_analysis"])
app.include_router(simple_analysis.router, prefix=settings.API_V1_STR + "/simple-analysis", tags=["simple_analysis"])


@app.on_event("startup")
async def startup_event():
    """Application startup - create tables if they don't exist"""
    create_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VerificAI Code Quality System API",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render uptime monitoring"""
    db_health = db_manager.health_check()
    return {
        "status": "healthy" if db_health else "unhealthy",
        "service": "verificai-backend",
        "database": "connected" if db_health else "disconnected"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    db_health = db_manager.health_check()
    return {
        "status": "ready" if db_health else "not_ready",
        "service": "verificai-backend",
        "database": "connected" if db_health else "disconnected"
    }


@app.get("/setup")
async def setup_first_admin():
    """
    One-time setup: creates the first admin user if no users exist.
    Access: GET /setup  (no auth required)
    Safe: returns error if any user already exists.
    """
    from app.core.database import get_db
    # Import ALL models to ensure SQLAlchemy mapper registry is complete
    from app.models.user import User, UserRole
    from app.models.code_entry import CodeEntry  # noqa: F401
    from app.models.analysis import Analysis, AnalysisResult  # noqa: F401
    from app.models.prompt import Prompt, PromptConfiguration  # noqa: F401
    from app.models.uploaded_file import UploadedFile  # noqa: F401
    from app.models.file_path import FilePath  # noqa: F401

    try:
        db = next(get_db())
        user_count = db.query(User).count()

        if user_count > 0:
            return {
                "success": False,
                "message": f"Setup already done. {user_count} user(s) exist.",
                "hint": "Use /api/v1/login with your credentials."
            }

        # Create first admin user
        admin = User(
            username="admin",
            email="admin@verificai.com",
            password="Admin@2024",
            full_name="Administrador VerificAI",
            role=UserRole.ADMIN,
            is_admin=True,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        return {
            "success": True,
            "message": "Admin user created successfully!",
            "credentials": {
                "username": "admin",
                "password": "Admin@2024",
                "email": "admin@verificai.com"
            },
            "next_step": "Login at your Vercel frontend or POST /api/v1/login"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/public/file-paths")
async def get_public_file_paths():
    """Get file paths for public access"""
    from app.core.database import get_db
    from app.models.file_path import FilePath
    from sqlalchemy import desc

    try:
        db = next(get_db())
        file_paths = db.query(FilePath).order_by(desc(FilePath.created_at)).all()
        paths = [fp.full_path for fp in file_paths if fp.full_path]
        return {
            "file_paths": paths,
            "total_count": len(paths),
            "message": f"Found {len(paths)} file paths"
        }
    except Exception as e:
        return {"file_paths": [], "total_count": 0, "message": "Error occurred"}


@app.options("/{path:path}")
async def options_handler(path: str):
    """Global OPTIONS handler for CORS preflight requests"""
    return {
        "message": "CORS preflight handled",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "headers": ["Content-Type", "Authorization"]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
