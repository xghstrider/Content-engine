"""
Base class for platform-specific content generators
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from content_engine.config.settings import get_settings
from content_engine.core.engine import ContentEngine
from content_engine.models.content import ContentRequest, ContentResponse, PlatformType
from content_engine.models.generation import GenerationConfig

logger = logging.getLogger(__name__)


class PlatformGenerator(ABC):
    """Abstract base class for platform-specific generators"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
        platform: Optional[Union[str, PlatformType]] = None,
    ):
        self.engine = engine or ContentEngine()
        self.settings = get_settings()
        
        if isinstance(platform, str):
            self.platform = PlatformType(platform)
        else:
            self.platform = platform or self.get_platform_type()
    
    @property
    @abstractmethod
    def get_platform_type(self) -> PlatformType:
        """Get the platform type"""
        pass
    
    @property
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the platform display name"""
        pass
    
    @property
    @abstractmethod
    def get_max_length(self) -> int:
        """Get the maximum content length for the platform"""
        pass
    
    @property
    @abstractmethod
    def get_hashtag_limit(self) -> int:
        """Get the hashtag limit for the platform"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate content for the platform"""
        pass
    
    @abstractmethod
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate content for multiple prompts"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming"""
        pass
    
    @abstractmethod
    def format_content(self, content: str, **kwargs) -> str:
        """Format content according to platform specifications"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content for the platform"""
        pass
    
    @abstractmethod
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get platform-specific default parameters"""
        pass
    
    async def generate_with_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        **kwargs,
    ) -> ContentResponse:
        """Generate content using a template"""
        # This will be implemented with the template system
        raise NotImplementedError("Template system not yet implemented")
    
    async def optimize_content(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize existing content for the platform"""
        prompt = f"Optimize this content for {self.get_platform_name()}: {content}"
        return await self.generate(prompt, **kwargs)
    
    async def analyze_content(
        self,
        content: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Analyze content for platform-specific metrics"""
        request = ContentRequest(
            prompt=f"Analyze this {self.platform.value} content",
            content_type="text",
            platform=self.platform,
        )
        return await self.engine.generator.provider.analyze(content, request)
    
    def _create_request(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentRequest:
        """Create a ContentRequest with platform defaults"""
        platform_params = self.get_platform_specific_params()
        
        # Merge platform defaults with provided kwargs
        merged_kwargs = {**platform_params, **kwargs}
        
        return ContentRequest(
            prompt=prompt,
            platform=self.platform,
            **merged_kwargs,
        )
