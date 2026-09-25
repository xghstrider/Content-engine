"""
Main entry point for Content Engine
"""

import asyncio
import logging
from typing import Optional

from content_engine.config.settings import get_settings
from content_engine.core.cache import ContentCache
from content_engine.core.engine import ContentEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global engine instance
_engine: Optional[ContentEngine] = None


def get_engine() -> ContentEngine:
    """Get or create the Content Engine instance"""
    global _engine
    if _engine is None:
        settings = get_settings()
        cache = ContentCache()
        _engine = ContentEngine(cache=cache)
    return _engine


async def generate(
    prompt: str,
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    **kwargs,
) -> dict:
    """
    Generate content with a simple interface
    
    Args:
        prompt: The main prompt or topic
        platform: Target platform (e.g., 'twitter', 'facebook', 'instagram')
        content_type: Type of content (e.g., 'text', 'social_post', 'blog_post')
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with generated content and metadata
    """
    engine = get_engine()
    response = await engine.generate(prompt, platform, content_type, **kwargs)
    return response.model_dump()


async def generate_batch(
    prompts: list,
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    **kwargs,
) -> list:
    """
    Generate content for multiple prompts
    
    Args:
        prompts: List of prompts
        platform: Target platform
        content_type: Type of content
        **kwargs: Additional parameters
        
    Returns:
        List of dictionaries with generated content and metadata
    """
    engine = get_engine()
    responses = await engine.generate_batch(prompts, platform, content_type, **kwargs)
    return [resp.model_dump() for resp in responses]


async def initialize() -> ContentEngine:
    """
    Initialize the Content Engine
    
    Returns:
        The initialized Content Engine instance
    """
    global _engine
    settings = get_settings()
    cache = ContentCache()
    _engine = ContentEngine(cache=cache)
    await _engine.initialize()
    return _engine


async def close() -> None:
    """Close the Content Engine and cleanup resources"""
    global _engine
    if _engine is not None:
        await _engine.close()
        _engine = None


# For backward compatibility
ContentEngine = ContentEngine
get_settings = get_settings
ContentCache = ContentCache


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Run CLI
        from content_engine.cli.commands import cli
        cli()
    else:
        # Run API server
        from content_engine.api.server import app
        import uvicorn
        
        settings = get_settings()
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
        )
