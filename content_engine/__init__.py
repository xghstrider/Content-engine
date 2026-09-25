"""
Content Engine - AI Powered Content Creation Platform

A comprehensive content generation engine for creating and customizing
all types of content, especially for social media platforms.
"""

__version__ = "1.0.0"
__author__ = "Content Engine Team"
__description__ = "AI Powered Content Engine for all types of content creation"

from content_engine.core.engine import ContentEngine
from content_engine.config.settings import Settings
from content_engine.models.content import ContentRequest, ContentResponse

__all__ = [
    "ContentEngine",
    "Settings",
    "ContentRequest",
    "ContentResponse",
]
