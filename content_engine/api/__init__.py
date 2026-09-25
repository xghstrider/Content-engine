"""
API module for Content Engine
"""

from content_engine.api.server import app
from content_engine.api.routes import router
from content_engine.api.handlers import (
    ContentHandler,
    PlatformHandler,
    TemplateHandler,
    GenerationHandler,
)

__all__ = [
    "app",
    "router",
    "ContentHandler",
    "PlatformHandler",
    "TemplateHandler",
    "GenerationHandler",
]
