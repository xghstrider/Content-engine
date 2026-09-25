"""
API routes for Content Engine
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from content_engine.api.handlers import (
    ContentHandler,
    PlatformHandler,
    TemplateHandler,
    GenerationHandler,
)

router = APIRouter()


# Content endpoints
@router.post("/content/generate", tags=["content"])
async def generate_content(
    request: dict,
    handler: ContentHandler = Depends(ContentHandler),
) -> dict:
    """Generate content from a request"""
    return await handler.generate_content(request)


@router.post("/content/generate_batch", tags=["content"])
async def generate_content_batch(
    requests: list,
    handler: ContentHandler = Depends(ContentHandler),
) -> list:
    """Generate content for multiple requests"""
    return await handler.generate_content_batch(requests)


@router.post("/content/stream", tags=["content"])
async def stream_content(
    request: dict,
    handler: ContentHandler = Depends(ContentHandler),
) -> StreamingResponse:
    """Generate content with streaming"""
    return await handler.stream_content(request)


@router.post("/content/regenerate", tags=["content"])
async def regenerate_content(
    response: dict,
    handler: ContentHandler = Depends(ContentHandler),
) -> dict:
    """Regenerate content with variations"""
    return await handler.regenerate_content(response)


@router.post("/content/alternatives", tags=["content"])
async def create_alternatives(
    request: dict,
    count: int = 3,
    handler: ContentHandler = Depends(ContentHandler),
) -> list:
    """Create multiple alternative versions of content"""
    return await handler.create_alternatives(request, count)


@router.post("/content/analyze", tags=["content"])
async def analyze_content(
    content: str,
    request: dict = None,
    handler: ContentHandler = Depends(ContentHandler),
) -> dict:
    """Analyze existing content"""
    return await handler.analyze_content(content, request or {})


# Platform-specific endpoints
@router.post("/platforms/twitter", tags=["platforms", "twitter"])
async def generate_twitter(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate Twitter/X content"""
    return await handler.generate_twitter(request)


@router.post("/platforms/facebook", tags=["platforms", "facebook"])
async def generate_facebook(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate Facebook content"""
    return await handler.generate_facebook(request)


@router.post("/platforms/instagram", tags=["platforms", "instagram"])
async def generate_instagram(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate Instagram content"""
    return await handler.generate_instagram(request)


@router.post("/platforms/linkedin", tags=["platforms", "linkedin"])
async def generate_linkedin(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate LinkedIn content"""
    return await handler.generate_linkedin(request)


@router.post("/platforms/pinterest", tags=["platforms", "pinterest"])
async def generate_pinterest(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate Pinterest content"""
    return await handler.generate_pinterest(request)


@router.post("/platforms/snapchat", tags=["platforms", "snapchat"])
async def generate_snapchat(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate Snapchat content"""
    return await handler.generate_snapchat(request)


@router.post("/platforms/website", tags=["platforms", "website"])
async def generate_website(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate website/blog content"""
    return await handler.generate_website(request)


@router.post("/platforms/email", tags=["platforms", "email"])
async def generate_email(
    request: dict,
    handler: PlatformHandler = Depends(PlatformHandler),
) -> dict:
    """Generate email content"""
    return await handler.generate_email(request)


# Template endpoints
@router.get("/templates", tags=["templates"])
async def list_templates(
    category: str = None,
    template_type: str = None,
    handler: TemplateHandler = Depends(TemplateHandler),
) -> list:
    """List all available templates"""
    return await handler.list_templates(category, template_type)


@router.get("/templates/{template_id}", tags=["templates"])
async def get_template(
    template_id: str,
    handler: TemplateHandler = Depends(TemplateHandler),
) -> dict:
    """Get a specific template"""
    return await handler.get_template(template_id)


@router.post("/templates/{template_id}/render", tags=["templates"])
async def render_template(
    template_id: str,
    variables: dict,
    handler: TemplateHandler = Depends(TemplateHandler),
) -> dict:
    """Render a template with variables"""
    return await handler.render_template(template_id, variables)


@router.post("/templates/search", tags=["templates"])
async def search_templates(
    query: str,
    limit: int = 10,
    handler: TemplateHandler = Depends(TemplateHandler),
) -> list:
    """Search templates by name or description"""
    return await handler.search_templates(query, limit)


# Generation endpoints
@router.get("/generation/stats", tags=["generation"])
async def get_generation_stats(
    handler: GenerationHandler = Depends(GenerationHandler),
) -> dict:
    """Get generation statistics"""
    return await handler.get_stats()


@router.post("/generation/cache/clear", tags=["generation", "cache"])
async def clear_cache(
    handler: GenerationHandler = Depends(GenerationHandler),
) -> dict:
    """Clear all cached content"""
    return await handler.clear_cache()


@router.get("/generation/cache/stats", tags=["generation", "cache"])
async def get_cache_stats(
    handler: GenerationHandler = Depends(GenerationHandler),
) -> dict:
    """Get cache statistics"""
    return await handler.get_cache_stats()


# Provider endpoints
@router.get("/providers", tags=["providers"])
async def get_providers(
    handler: GenerationHandler = Depends(GenerationHandler),
) -> dict:
    """Get available AI providers"""
    return await handler.get_providers()


@router.get("/providers/current", tags=["providers"])
async def get_current_provider(
    handler: GenerationHandler = Depends(GenerationHandler),
) -> dict:
    """Get current provider information"""
    return await handler.get_current_provider()


@router.post("/providers/change", tags=["providers"])
async def change_provider(
    provider: str,
    handler: GenerationHandler = Depends(GenerationHandler),
) -> dict:
    """Change the AI provider"""
    return await handler.change_provider(provider)


# Content type endpoints
@router.post("/content/twitter", tags=["content", "twitter"])
async def generate_twitter_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate Twitter/X content (simplified)"""
    return await handler.generate_twitter_content(prompt, **kwargs)


@router.post("/content/facebook", tags=["content", "facebook"])
async def generate_facebook_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate Facebook content (simplified)"""
    return await handler.generate_facebook_content(prompt, **kwargs)


@router.post("/content/instagram", tags=["content", "instagram"])
async def generate_instagram_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate Instagram content (simplified)"""
    return await handler.generate_instagram_content(prompt, **kwargs)


@router.post("/content/linkedin", tags=["content", "linkedin"])
async def generate_linkedin_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate LinkedIn content (simplified)"""
    return await handler.generate_linkedin_content(prompt, **kwargs)


@router.post("/content/pinterest", tags=["content", "pinterest"])
async def generate_pinterest_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate Pinterest content (simplified)"""
    return await handler.generate_pinterest_content(prompt, **kwargs)


@router.post("/content/snapchat", tags=["content", "snapchat"])
async def generate_snapchat_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate Snapchat content (simplified)"""
    return await handler.generate_snapchat_content(prompt, **kwargs)


@router.post("/content/website", tags=["content", "website"])
async def generate_website_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate website/blog content (simplified)"""
    return await handler.generate_website_content(prompt, **kwargs)


@router.post("/content/email", tags=["content", "email"])
async def generate_email_content(
    prompt: str,
    handler: ContentHandler = Depends(ContentHandler),
    **kwargs,
) -> dict:
    """Generate email content (simplified)"""
    return await handler.generate_email_content(prompt, **kwargs)
