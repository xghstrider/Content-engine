"""
API request handlers for Content Engine
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse

from content_engine.config.providers import DEFAULT_PROVIDERS, ProviderType
from content_engine.core.cache import ContentCache
from content_engine.core.engine import ContentEngine
from content_engine.models.content import ContentRequest, ContentResponse
from content_engine.models.generation import GenerationConfig
from content_engine.models.templates import Template, TemplateCategory, TemplateType
from content_engine.platforms import (
    TwitterGenerator,
    FacebookGenerator,
    InstagramGenerator,
    LinkedInGenerator,
    PinterestGenerator,
    SnapchatGenerator,
    WebsiteGenerator,
    EmailGenerator,
)
from content_engine.templates.manager import TemplateManager

logger = logging.getLogger(__name__)


def get_engine_dependency() -> ContentEngine:
    """Lazily resolve the initialized engine without circular imports."""
    from content_engine.api.server import get_engine

    return get_engine()


class ContentHandler:
    """Handler for content generation requests"""
    
    def __init__(self, engine: ContentEngine = Depends(get_engine_dependency)):
        self.engine = engine
    
    async def generate_content(self, request_data: dict) -> dict:
        """Handle content generation request"""
        try:
            # Convert request data to ContentRequest
            request = ContentRequest(**request_data)
            
            # Generate content
            response = await self.engine.generate_advanced(request)
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_content_batch(self, requests_data: list) -> list:
        """Handle batch content generation"""
        try:
            requests = [ContentRequest(**req) for req in requests_data]
            responses = await self.engine.generate_batch(requests)
            return [resp.model_dump() for resp in responses]
        except Exception as e:
            logger.error(f"Batch generation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def stream_content(self, request_data: dict) -> StreamingResponse:
        """Handle streaming content generation"""
        try:
            request = ContentRequest(**request_data)
            
            async def generate():
                async for chunk in self.engine.generate_stream(
                    request.prompt,
                    platform=request.platform.value if request.platform else None,
                    content_type=request.content_type.value if request.content_type else None,
                ):
                    yield chunk
            
            return StreamingResponse(generate(), media_type="text/plain")
            
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def regenerate_content(self, response_data: dict) -> dict:
        """Handle content regeneration"""
        try:
            response = ContentResponse(**response_data)
            regenerated = await self.engine.regenerate(response)
            return regenerated.model_dump()
        except Exception as e:
            logger.error(f"Regeneration failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_alternatives(self, request_data: dict, count: int = 3) -> list:
        """Handle alternative generation"""
        try:
            request = ContentRequest(**request_data)
            alternatives = await self.engine.create_alternatives(request, count)
            return [alt.model_dump() for alt in alternatives]
        except Exception as e:
            logger.error(f"Alternative generation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def analyze_content(self, content: str, request_data: dict) -> dict:
        """Handle content analysis"""
        try:
            request = ContentRequest(**request_data)
            analysis = await self.engine.analyze_content(content)
            return analysis
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # Simplified platform-specific methods
    async def generate_twitter_content(self, prompt: str, **kwargs) -> dict:
        """Generate Twitter content"""
        try:
            response = await self.engine.generate_twitter(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_facebook_content(self, prompt: str, **kwargs) -> dict:
        """Generate Facebook content"""
        try:
            response = await self.engine.generate_facebook(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_instagram_content(self, prompt: str, **kwargs) -> dict:
        """Generate Instagram content"""
        try:
            response = await self.engine.generate_instagram(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_linkedin_content(self, prompt: str, **kwargs) -> dict:
        """Generate LinkedIn content"""
        try:
            response = await self.engine.generate_linkedin(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_pinterest_content(self, prompt: str, **kwargs) -> dict:
        """Generate Pinterest content"""
        try:
            response = await self.engine.generate_pinterest(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_snapchat_content(self, prompt: str, **kwargs) -> dict:
        """Generate Snapchat content"""
        try:
            response = await self.engine.generate_snapchat(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_website_content(self, prompt: str, **kwargs) -> dict:
        """Generate website content"""
        try:
            response = await self.engine.generate_website(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def generate_email_content(self, prompt: str, **kwargs) -> dict:
        """Generate email content"""
        try:
            response = await self.engine.generate_email(prompt, **kwargs)
            return response.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


class PlatformHandler:
    """Handler for platform-specific requests"""
    
    def __init__(self, engine: ContentEngine = Depends(get_engine_dependency)):
        self.engine = engine
        self._generators = {}
    
    async def _get_generator(self, platform: str):
        """Get or create a platform generator"""
        if platform not in self._generators:
            if platform == "twitter":
                self._generators[platform] = TwitterGenerator(self.engine)
            elif platform == "facebook":
                self._generators[platform] = FacebookGenerator(self.engine)
            elif platform == "instagram":
                self._generators[platform] = InstagramGenerator(self.engine)
            elif platform == "linkedin":
                self._generators[platform] = LinkedInGenerator(self.engine)
            elif platform == "pinterest":
                self._generators[platform] = PinterestGenerator(self.engine)
            elif platform == "snapchat":
                self._generators[platform] = SnapchatGenerator(self.engine)
            elif platform == "website" or platform == "web":
                self._generators[platform] = WebsiteGenerator(self.engine)
            elif platform == "email":
                self._generators[platform] = EmailGenerator(self.engine)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")
        
        return self._generators[platform]
    
    async def generate_twitter(self, request_data: dict) -> dict:
        """Generate Twitter content"""
        generator = await self._get_generator("twitter")
        response = await generator.generate(**request_data)
        return response.model_dump()
    
    async def generate_facebook(self, request_data: dict) -> dict:
        """Generate Facebook content"""
        generator = await self._get_generator("facebook")
        response = await generator.generate(**request_data)
        return response.model_dump()
    
    async def generate_instagram(self, request_data: dict) -> dict:
        """Generate Instagram content"""
        generator = await self._get_generator("instagram")
        response = await generator.generate(**request_data)
        return response.model_dump()
    
    async def generate_linkedin(self, request_data: dict) -> dict:
        """Generate LinkedIn content"""
        generator = await self._get_generator("linkedin")
        response = await generator.generate(**request_data)
        return response.model_dump()
    
    async def generate_pinterest(self, request_data: dict) -> dict:
        """Generate Pinterest content"""
        generator = await self._get_generator("pinterest")
        response = await generator.generate(**request_data)
        return response.model_dump()
    
    async def generate_snapchat(self, request_data: dict) -> dict:
        """Generate Snapchat content"""
        generator = await self._get_generator("snapchat")
        response = await generator.generate(**request_data)
        return response.model_dump()


class TemplateHandler:
    """Handler for template requests"""
    
    def __init__(self, engine: ContentEngine = Depends(get_engine_dependency)):
        self.engine = engine
        self.template_manager = TemplateManager()
    
    async def list_templates(
        self,
        category: Optional[str] = None,
        template_type: Optional[str] = None,
    ) -> list:
        """List all templates"""
        try:
            templates = await self.template_manager.list_templates(
                category=TemplateCategory(category) if category else None,
                template_type=TemplateType(template_type) if template_type else None,
            )
            return [t.model_dump() for t in templates]
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_template(self, template_id: str) -> dict:
        """Get a specific template"""
        try:
            template = await self.template_manager.get_template(template_id)
            if not template:
                raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
            return template.model_dump()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get template: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def render_template(self, template_id: str, variables: dict) -> dict:
        """Render a template with variables"""
        try:
            content = await self.template_manager.render_template(template_id, variables)
            return {"content": content}
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def search_templates(self, query: str, limit: int = 10) -> list:
        """Search templates"""
        try:
            templates = await self.template_manager.search_templates(query, limit)
            return [t.model_dump() for t in templates]
        except Exception as e:
            logger.error(f"Failed to search templates: {e}")
            raise HTTPException(status_code=400, detail=str(e))


class GenerationHandler:
    """Handler for generation management requests"""
    
    def __init__(self, engine: ContentEngine = Depends(get_engine_dependency)):
        self.engine = engine
    
    async def get_stats(self) -> dict:
        """Get engine statistics"""
        try:
            stats = await self.engine.get_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def clear_cache(self) -> dict:
        """Clear all cached content"""
        try:
            count = await self.engine.clear_cache()
            return {"message": f"Cleared {count} cached items", "count": count}
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        try:
            stats = await self.engine.get_cache_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_providers(self) -> dict:
        """Get available AI providers"""
        try:
            providers = list(DEFAULT_PROVIDERS.keys())
            return {
                "providers": providers,
                "default": self.engine.settings.ai.default_provider,
            }
        except Exception as e:
            logger.error(f"Failed to get providers: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_current_provider(self) -> dict:
        """Get current provider information"""
        try:
            info = await self.engine.get_provider_info()
            return info
        except Exception as e:
            logger.error(f"Failed to get current provider: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def change_provider(self, provider: str) -> dict:
        """Change the AI provider"""
        try:
            await self.engine.change_provider(provider)
            return {"message": f"Provider changed to {provider}", "provider": provider}
        except Exception as e:
            logger.error(f"Failed to change provider: {e}")
            raise HTTPException(status_code=400, detail=str(e))
