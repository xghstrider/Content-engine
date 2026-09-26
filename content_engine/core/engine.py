"""
Main Content Engine implementation
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from content_engine.config.settings import get_settings
from content_engine.config.web_configuration import web_configuration
from content_engine.core.cache import ContentCache
from content_engine.core.generator import ContentGenerator
from content_engine.core.providers import AIProvider, ProviderFactory
from content_engine.models.content import ContentRequest, ContentResponse
from content_engine.models.generation import GenerationConfig

logger = logging.getLogger(__name__)


class ContentEngine:
    """
    Main Content Engine class
    
    This is the primary interface for generating content using AI.
    It supports multiple platforms and content types with extensive customization.
    """
    
    def __init__(
        self,
        provider: Optional[Union[str, AIProvider]] = None,
        cache: Optional[ContentCache] = None,
    ):
        """
        Initialize the Content Engine
        
        Args:
            provider: AI provider to use (string name or AIProvider instance)
            cache: ContentCache instance for caching results
        """
        self.settings = get_settings()
        self.cache = cache or ContentCache()
        self.generator = ContentGenerator(provider, self.cache)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the engine"""
        if self._initialized:
            return
        
        logger.info("Initializing Content Engine...")
        
        # Initialize cache
        if self.settings.cache.cache_enabled:
            await self.cache.cleanup()
        
        self._initialized = True
        logger.info("Content Engine initialized successfully")
    
    async def close(self) -> None:
        """Close the engine and cleanup resources"""
        logger.info("Closing Content Engine...")
        
        # Close the provider
        await self.generator.provider.close()
        
        # Clear cache
        if self.settings.cache.cache_enabled:
            await self.cache.clear()
        
        self._initialized = False
        logger.info("Content Engine closed")
    
    async def generate(
        self,
        prompt: str,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ) -> ContentResponse:
        """
        Generate content with a simple interface
        
        Args:
            prompt: The main prompt or topic
            platform: Target platform (e.g., 'twitter', 'facebook', 'instagram')
            content_type: Type of content (e.g., 'text', 'social_post', 'blog_post')
            **kwargs: Additional parameters for ContentRequest
            
        Returns:
            ContentResponse with generated content
        """
        await self.initialize()
        
        # Create request
        request = ContentRequest(
            prompt=prompt,
            platform=platform,
            content_type=content_type,
            **kwargs,
        )
        
        return await self.generator.generate(request)
    
    async def generate_advanced(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None,
    ) -> ContentResponse:
        """
        Generate content with full control
        
        Args:
            request: ContentRequest with all generation parameters
            config: GenerationConfig for AI provider settings
            
        Returns:
            ContentResponse with generated content
        """
        await self.initialize()
        return await self.generator.generate(request, config)
    
    async def generate_batch(
        self,
        prompts: List[str],
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        max_concurrent: int = 5,
        **kwargs,
    ) -> List[ContentResponse]:
        """
        Generate content for multiple prompts
        
        Args:
            prompts: List of prompts
            platform: Target platform
            content_type: Type of content
            max_concurrent: Maximum concurrent generations
            **kwargs: Additional parameters for ContentRequest
            
        Returns:
            List of ContentResponse objects
        """
        await self.initialize()
        
        requests = [
            ContentRequest(
                prompt=prompt,
                platform=platform,
                content_type=content_type,
                **kwargs,
            )
            for prompt in prompts
        ]
        
        return await self.generator.generate_batch(requests, max_concurrent=max_concurrent)
    
    async def generate_stream(
        self,
        prompt: str,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate content with streaming
        
        Args:
            prompt: The main prompt or topic
            platform: Target platform
            content_type: Type of content
            **kwargs: Additional parameters for ContentRequest
            
        Yields:
            Chunks of generated content as they arrive
        """
        await self.initialize()
        
        request = ContentRequest(
            prompt=prompt,
            platform=platform,
            content_type=content_type,
            **kwargs,
        )
        
        async for chunk in self.generator.generate_stream(request):
            yield chunk
    
    async def create_alternatives(
        self,
        prompt: str,
        count: int = 3,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ) -> List[ContentResponse]:
        """
        Create multiple alternative versions of content
        
        Args:
            prompt: The main prompt or topic
            count: Number of alternatives to generate
            platform: Target platform
            content_type: Type of content
            **kwargs: Additional parameters for ContentRequest
            
        Returns:
            List of ContentResponse objects with different variations
        """
        await self.initialize()
        
        request = ContentRequest(
            prompt=prompt,
            platform=platform,
            content_type=content_type,
            **kwargs,
        )
        
        return await self.generator.create_alternatives(request, count)
    
    async def regenerate(
        self,
        response: ContentResponse,
        **kwargs,
    ) -> ContentResponse:
        """
        Regenerate content with variations
        
        Args:
            response: Previous ContentResponse to regenerate
            **kwargs: Additional parameters to modify the request
            
        Returns:
            New ContentResponse with regenerated content
        """
        await self.initialize()
        
        # Create a new request based on the response
        request = ContentRequest(
            prompt=response.metadata.get('original_prompt', response.content[:100]),
            platform=response.platform,
            content_type=response.content_type,
            **kwargs,
        )
        
        return await self.generator.regenerate(request, response)
    
    # Convenience methods for specific platforms
    
    async def generate_twitter(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Twitter/X content"""
        return await self.generate(
            prompt,
            platform="twitter",
            content_type="social_post",
            **kwargs,
        )
    
    async def generate_facebook(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Facebook content"""
        return await self.generate(
            prompt,
            platform="facebook",
            content_type="social_post",
            **kwargs,
        )
    
    async def generate_instagram(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Instagram content"""
        return await self.generate(
            prompt,
            platform="instagram",
            content_type="social_post",
            **kwargs,
        )
    
    async def generate_linkedin(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate LinkedIn content"""
        return await self.generate(
            prompt,
            platform="linkedin",
            content_type="social_post",
            **kwargs,
        )
    
    async def generate_pinterest(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Pinterest content"""
        return await self.generate(
            prompt,
            platform="pinterest",
            content_type="social_post",
            **kwargs,
        )
    
    async def generate_snapchat(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Snapchat content"""
        return await self.generate(
            prompt,
            platform="snapchat",
            content_type="social_post",
            **kwargs,
        )
    
    async def generate_website(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate website/blog content"""
        return await self.generate(
            prompt,
            platform="web",
            content_type="blog_post",
            **kwargs,
        )
    
    async def generate_email(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate email content"""
        return await self.generate(
            prompt,
            platform="email",
            content_type="email",
            **kwargs,
        )
    
    async def generate_ad_copy(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate advertising copy"""
        return await self.generate(
            prompt,
            content_type="ad_copy",
            **kwargs,
        )
    
    async def generate_product_description(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate product description"""
        return await self.generate(
            prompt,
            content_type="product_description",
            **kwargs,
        )
    
    async def generate_seo_content(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate SEO-optimized content"""
        return await self.generate(
            prompt,
            content_type="seo_content",
            **kwargs,
        )
    
    # Cache management
    
    async def clear_cache(self) -> int:
        """Clear all cached content"""
        return await self.cache.clear()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return await self.cache.get_stats()
    
    # Provider management
    
    async def change_provider(self, provider: Union[str, AIProvider]) -> None:
        """Change the AI provider"""
        if isinstance(provider, str):
            if provider in web_configuration.list_providers() or provider in {"openai", "anthropic", "google", "local"}:
                self.settings.ai.default_provider = provider
                if provider in web_configuration.list_providers():
                    web_configuration.set_default_provider(provider)
            self.generator.provider = ProviderFactory.create_provider(provider)
        else:
            self.generator.provider = provider
    
    async def get_provider_info(self) -> Dict[str, Any]:
        """Get current provider information"""
        return {
            "provider": self.generator.provider.config.provider_type.value,
            "model": self.generator.provider.config.model,
            "base_url": self.generator.provider.config.base_url,
        }
    
    # Utility methods
    
    async def analyze_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analyze existing content"""
        request = ContentRequest(
            prompt="Analyze this content",
            content_type="text",
            **kwargs,
        )
        return await self.generator.provider.analyze(content, request)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "initialized": self._initialized,
            "provider": self.generator.provider.config.provider_type.value,
            "model": self.generator.provider.config.model,
            "cache_stats": await self.cache.get_stats(),
        }
