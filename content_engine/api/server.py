"""
FastAPI server for Content Engine
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from content_engine.config.settings import get_settings, Settings
from content_engine.core.cache import ContentCache
from content_engine.core.engine import ContentEngine
from content_engine.api.routes import router as api_router

logger = logging.getLogger(__name__)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

# Global instances
_engine: Optional[ContentEngine] = None
_settings: Optional[Settings] = None
_cache: Optional[ContentCache] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    global _engine, _settings, _cache
    
    # Startup
    logger.info("Starting Content Engine API...")
    
    # Initialize settings
    _settings = get_settings()
    logger.info(f"Settings loaded: {_settings.app_name} v{_settings.app_version}")
    
    # Initialize cache
    _cache = ContentCache()
    logger.info("Cache initialized")
    
    # Initialize engine
    _engine = ContentEngine(cache=_cache)
    await _engine.initialize()
    logger.info("Content Engine initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Content Engine API...")
    
    if _engine:
        await _engine.close()
    
    if _cache:
        await _cache.clear()
    
    logger.info("Content Engine API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Content Engine API",
    description="AI Powered Content Engine for all types of content creation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> FileResponse:
    """Serve the browser workspace."""
    return FileResponse(WEB_DIR / "index.html")


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "engine": "running" if _engine else "stopped",
    }


# Error handlers
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    logger.error(f"Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
        },
    )


# Get engine instance
def get_engine() -> ContentEngine:
    """Get the Content Engine instance"""
    if _engine is None:
        raise RuntimeError("Content Engine not initialized")
    return _engine


# Get settings instance
def get_api_settings() -> Settings:
    """Get the settings instance"""
    if _settings is None:
        raise RuntimeError("Settings not initialized")
    return _settings
