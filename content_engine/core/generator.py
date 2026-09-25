"""
Content Generator implementation
"""

import asyncio
import hashlib
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from content_engine.config.settings import get_settings
from content_engine.core.cache import ContentCache
from content_engine.core.providers import ProviderFactory, AIProvider
from content_engine.models.content import ContentRequest, ContentResponse, ContentType
from content_engine.models.generation import GenerationConfig, GenerationResult, GenerationStatus

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Main content generator class"""
    
    def __init__(
        self,
        provider: Optional[Union[str, AIProvider]] = None,
        cache: Optional[ContentCache] = None,
    ):
        self.settings = get_settings()
        self.cache = cache or ContentCache()
        
        # Initialize provider
        if isinstance(provider, str):
            self.provider: AIProvider = ProviderFactory.create_provider(provider)
        elif provider is not None:
            self.provider = provider
        else:
            self.provider = ProviderFactory.create_provider(self.settings.ai.default_provider)
        
        self._generation_count = 0
    
    async def generate(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None,
    ) -> ContentResponse:
        """Generate content from a request"""
        start_time = time.time()
        
        # Create generation config
        gen_config = config or GenerationConfig()
        
        # Check cache
        cache_key = self._get_cache_key(request, gen_config)
        if gen_config.use_cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for request: {cache_key[:16]}...")
                return ContentResponse(**cached)
        
        # Generate unique IDs
        request_id = f"req_{int(time.time() * 1000)}_{self._generation_count}"
        self._generation_count += 1
        
        # Generate content
        try:
            content = await self._generate_content(request, gen_config)
            
            # Analyze the content
            analysis = await self._analyze_content(content, request)
            
            # Create response
            response = ContentResponse(
                content=content,
                content_type=request.content_type,
                platform=request.platform,
                request_id=request_id,
                session_id=request.session_id,
                user_id=request.user_id,
                provider=self.provider.config.provider_type.value,
                model=self.provider.config.model,
                generation_time=time.time() - start_time,
                timestamp=datetime.utcnow(),
                quality_score=analysis.get("quality_score"),
                readability_score=analysis.get("readability_score"),
                sentiment=analysis.get("sentiment"),
                tone=analysis.get("tone"),
                keywords_used=analysis.get("keywords", []),
                hashtags=analysis.get("hashtags", []),
                character_count=len(content),
                word_count=len(content.split()),
                sentence_count=content.count(".") + content.count("!") + content.count("?"),
                paragraph_count=content.count("\n\n") + 1,
                metadata={
                    "tokens_used": analysis.get("tokens_used", 0),
                    "provider": self.provider.config.provider_type.value,
                    "model": self.provider.config.model,
                },
                warnings=analysis.get("warnings", []),
                suggestions=analysis.get("suggestions", []),
            )
            
            # Cache the result
            if gen_config.use_cache and len(content) < self.settings.cache.max_cache_size:
                await self.cache.set(
                    cache_key,
                    response.model_dump(),
                    ttl=gen_config.cache_ttl or self.settings.cache.cache_ttl
                )
            
            logger.info(f"Generated content for request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    async def generate_batch(
        self,
        requests: List[ContentRequest],
        config: Optional[GenerationConfig] = None,
        max_concurrent: int = 5,
    ) -> List[ContentResponse]:
        """Generate content for multiple requests in batch"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_request(request: ContentRequest) -> ContentResponse:
            async with semaphore:
                return await self.generate(request, config)
        
        tasks = [process_request(req) for req in requests]
        return await asyncio.gather(*tasks)
    
    async def generate_stream(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming"""
        gen_config = config or GenerationConfig(use_streaming=True)
        
        try:
            async for chunk in self.provider.generate_stream(request, gen_config):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise
    
    async def regenerate(
        self,
        request: ContentRequest,
        response: ContentResponse,
        config: Optional[GenerationConfig] = None,
    ) -> ContentResponse:
        """Regenerate content with slight variations"""
        # Modify the request slightly for variation
        modified_request = ContentRequest(
            **request.model_dump(),
            temperature=(request.temperature or 0.7) + 0.1,  # Increase creativity
        )
        
        # Disable cache for regeneration
        gen_config = config or GenerationConfig(use_cache=False)
        
        return await self.generate(modified_request, gen_config)
    
    async def create_alternatives(
        self,
        request: ContentRequest,
        count: int = 3,
        config: Optional[GenerationConfig] = None,
    ) -> List[ContentResponse]:
        """Create multiple alternative versions of content"""
        responses = []
        
        for i in range(count):
            # Modify temperature for each alternative
            modified_request = ContentRequest(
                **request.model_dump(),
                temperature=0.5 + (i * 0.1),  # Vary temperature
            )
            
            gen_config = config or GenerationConfig(use_cache=False)
            response = await self.generate(modified_request, gen_config)
            responses.append(response)
        
        return responses
    
    def _get_cache_key(self, request: ContentRequest, config: GenerationConfig) -> str:
        """Generate a cache key for the request"""
        data = {
            "prompt": request.prompt,
            "content_type": request.content_type.value,
            "platform": request.platform.value if request.platform else None,
            "tone": request.tone.value if request.tone else None,
            "style": request.style.value if request.style else None,
            "quality": request.quality.value,
            "keywords": request.keywords,
            "min_length": request.min_length,
            "max_length": request.max_length,
            "use_markdown": request.use_markdown,
            "use_emojis": request.use_emojis,
            "use_hashtags": request.use_hashtags,
            "hashtag_count": request.hashtag_count,
            "language": request.language,
            "provider": config.provider if config else self.settings.ai.default_provider,
            "model": config.model if config else self.provider.config.model,
            "temperature": config.temperature if config else self.provider.config.temperature,
        }
        
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _generate_content(
        self,
        request: ContentRequest,
        config: GenerationConfig,
    ) -> str:
        """Internal method to generate content"""
        retries = 0
        max_retries = config.max_retries or self.provider.config.max_retries
        
        while retries < max_retries:
            try:
                content = await self.provider.generate(request, config)
                
                # Validate the content
                if self._validate_content(content, request):
                    return content
                
                retries += 1
                logger.warning(f"Content validation failed, retry {retries}/{max_retries}")
                
                if retries < max_retries:
                    await asyncio.sleep(config.retry_delay or self.provider.config.timeout)
                    
            except Exception as e:
                retries += 1
                logger.error(f"Generation attempt {retries} failed: {e}")
                
                if retries < max_retries:
                    await asyncio.sleep(config.retry_delay or self.provider.config.timeout)
        
        raise RuntimeError(f"Failed to generate valid content after {max_retries} attempts")
    
    async def _analyze_content(
        self,
        content: str,
        request: ContentRequest,
    ) -> Dict[str, Any]:
        """Analyze the generated content"""
        try:
            analysis = await self.provider.analyze(content, request)
            return analysis
        except Exception as e:
            logger.warning(f"Content analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "tone": request.tone.value if request.tone else "neutral",
                "keywords": request.keywords,
                "hashtags": [],
                "readability_score": 0.7,
                "quality_score": 0.7,
                "warnings": [f"Analysis failed: {str(e)}"],
                "suggestions": [],
            }
    
    def _validate_content(self, content: str, request: ContentRequest) -> bool:
        """Validate the generated content"""
        if not content or not content.strip():
            return False
        
        # Check length constraints
        if request.min_length and len(content) < request.min_length:
            return False
        
        if request.max_length and len(content) > request.max_length:
            return False
        
        # Check for required keywords
        if request.keywords:
            for keyword in request.keywords:
                if keyword.lower() not in content.lower():
                    return False
        
        return True
