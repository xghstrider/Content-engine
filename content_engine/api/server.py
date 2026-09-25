"""
FastAPI server for Content Engine
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from content_engine.config.settings import get_settings, Settings
from content_engine.core.cache import ContentCache
from content_engine.core.engine import ContentEngine
from content_engine.api.routes import router as api_router

logger = logging.getLogger(__name__)

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


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> HTMLResponse:
    """Serve a simple browser UI for the local tool."""
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Content Engine</title>
            <style>
                :root {
                    --bg: #061a15;
                    --panel: #0d2b26;
                    --panel-border: #1d4d45;
                    --text: #eafaf5;
                    --muted: #a8d7c9;
                    --accent: #63f6be;
                    --accent-2: #6dc6ff;
                }
                * { box-sizing: border-box; }
                body {
                    margin: 0;
                    font-family: Arial, Helvetica, sans-serif;
                    background: linear-gradient(135deg, #071712, #0d2b26 50%, #0a1d1a);
                    color: var(--text);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .card {
                    width: min(760px, 90vw);
                    background: rgba(13, 43, 38, 0.9);
                    border: 1px solid var(--panel-border);
                    border-radius: 18px;
                    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
                    padding: 32px 28px;
                }
                h1 {
                    margin: 0 0 10px;
                    font-size: clamp(2rem, 4vw, 3rem);
                    letter-spacing: 0.04em;
                }
                p {
                    margin: 0 0 20px;
                    color: var(--muted);
                    line-height: 1.6;
                    font-size: 1.05rem;
                }
                .actions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-top: 24px;
                }
                a.button {
                    display: inline-block;
                    text-decoration: none;
                    padding: 12px 18px;
                    border-radius: 10px;
                    border: 1px solid transparent;
                    font-weight: 700;
                    transition: 0.2s ease;
                }
                .primary {
                    background: var(--accent);
                    color: #062f23;
                }
                .secondary {
                    color: var(--text);
                    background: rgba(255,255,255,0.03);
                    border-color: var(--panel-border);
                }
                a.button:hover { transform: translateY(-1px); }
                .status {
                    margin-top: 18px;
                    background: rgba(99, 246, 190, 0.08);
                    border: 1px solid rgba(99, 246, 190, 0.2);
                    border-radius: 10px;
                    padding: 12px 14px;
                    color: var(--accent);
                    font-weight: 600;
                }
            </style>
        </head>
        <body>
            <main class="card">
                <h1>Content Engine</h1>
                <p>AI-powered content generation for marketing, social media, and website copy.</p>
                <div class="status" id="status">Checking local API health…</div>
                <div class="actions">
                    <a class="button primary" href="/docs">Open API Docs</a>
                    <a class="button secondary" href="/health">Health Check</a>
                </div>
            </main>
            <script>
                fetch('/health')
                    .then((res) => res.json())
                    .then((data) => {
                        document.getElementById('status').textContent = 'API status: ' + data.status + ' • version ' + data.version;
                    })
                    .catch(() => {
                        document.getElementById('status').textContent = 'API unavailable; start the server and refresh.';
                    });
            </script>
        </body>
        </html>
        """
    )


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
