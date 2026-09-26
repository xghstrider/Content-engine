"""
AI Provider implementations
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import httpx

from content_engine.config.providers import AIProviderConfig, ProviderType
from content_engine.config.settings import get_settings
from content_engine.config.web_configuration import web_configuration
from content_engine.models.content import ContentRequest
from content_engine.models.generation import GenerationConfig

logger = logging.getLogger(__name__)
settings = get_settings()


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the provider"""
        self.client = httpx.AsyncClient(
            timeout=self.config.timeout,
            follow_redirects=True,
        )
    
    @abstractmethod
    async def generate(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate content from a request"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming"""
        pass
    
    @abstractmethod
    async def analyze(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Analyze generated content"""
        pass
    
    async def close(self) -> None:
        """Close the provider connection"""
        if self.client:
            await self.client.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(self.close())


class OpenAIProvider(AIProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: AIProviderConfig):
        if config.provider_type != ProviderType.OPENAI:
            config.provider_type = ProviderType.OPENAI
        super().__init__(config)
    
    async def generate(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate content using OpenAI API"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Build the prompt
        prompt = self._build_prompt(request)
        
        # Get generation config
        gen_config = config or GenerationConfig()
        
        # Prepare request data
        data = {
            "model": gen_config.model or self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": gen_config.temperature or self.config.temperature,
            "max_tokens": gen_config.max_tokens or self.config.max_tokens,
            "top_p": gen_config.top_p or self.config.top_p,
            "frequency_penalty": gen_config.frequency_penalty or self.config.frequency_penalty,
            "presence_penalty": gen_config.presence_penalty or self.config.presence_penalty,
        }
        
        # Add custom parameters
        if gen_config.custom_parameters:
            data.update(gen_config.custom_parameters)
        
        # Make the request
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def generate_stream(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming using OpenAI API"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        data = {
            "model": gen_config.model or self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": gen_config.temperature or self.config.temperature,
            "max_tokens": gen_config.max_tokens or self.config.max_tokens,
            "stream": True,
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=data,
            ) as response:
                async for line in response.aiter_lines():
                    if line and line.strip():
                        try:
                            chunk = json.loads(line)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                content = chunk["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                        
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise
    
    async def analyze(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Analyze content using OpenAI API"""
        analysis_prompt = f"""Analyze the following content and provide:
1. Sentiment (positive, negative, neutral)
2. Tone (from: professional, casual, friendly, formal, humorous, sarcastic, inspirational, educational, promotional, storytelling, conversational, technical, persuasive, emotional)
3. Keywords (list of main keywords)
4. Readability score (0-1)
5. Quality score (0-1)
6. Suggestions for improvement (list)

Content:
{content}

Provide the analysis as JSON."""
        
        try:
            analysis = await self.generate(
                ContentRequest(prompt=analysis_prompt),
                GenerationConfig(
                    model=self.config.model,
                    temperature=0.3,
                    max_tokens=500,
                )
            )
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Failed to parse analysis"}
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}
    
    def _build_prompt(self, request: ContentRequest) -> str:
        """Build the prompt from a content request"""
        prompt_parts = []
        
        # Add context if provided
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        
        # Add keywords
        if request.keywords:
            prompt_parts.append(f"Keywords to include: {', '.join(request.keywords)}")
        
        # Add platform-specific instructions
        if request.platform:
            prompt_parts.append(f"Platform: {request.platform.value}")
        
        # Add content type
        prompt_parts.append(f"Content type: {request.content_type.value}")
        
        # Add tone and style
        if request.tone:
            prompt_parts.append(f"Tone: {request.tone.value}")
        if request.style:
            prompt_parts.append(f"Style: {request.style.value}")
        
        # Add length constraints
        if request.min_length or request.max_length:
            constraints = []
            if request.min_length:
                constraints.append(f"minimum {request.min_length} characters")
            if request.max_length:
                constraints.append(f"maximum {request.max_length} characters")
            prompt_parts.append(f"Length: {', '.join(constraints)}")
        
        # Add formatting options
        formatting = []
        if request.use_markdown:
            formatting.append("use Markdown formatting")
        if request.use_emojis:
            formatting.append("include emojis")
        if request.use_hashtags:
            if request.hashtag_count:
                formatting.append(f"include {request.hashtag_count} hashtags")
            else:
                formatting.append("include hashtags")
        if formatting:
            prompt_parts.append(f"Formatting: {', '.join(formatting)}")
        
        # Add custom instructions
        if request.custom_instructions:
            prompt_parts.append(f"Instructions: {request.custom_instructions}")
        
        # Add target audience
        if request.target_audience:
            prompt_parts.append(f"Target audience: {request.target_audience}")
        
        # Add language
        prompt_parts.append(f"Language: {request.language}")
        
        # Combine all parts
        context = "\n".join(prompt_parts) if prompt_parts else ""
        
        return f"""Create {request.content_type.value} content for {request.platform.value if request.platform else 'general use'}.

{context}

Prompt: {request.prompt}

Generate high-quality content that follows all the above specifications."""


class AnthropicProvider(AIProvider):
    """Anthropic API provider"""
    
    def __init__(self, config: AIProviderConfig):
        if config.provider_type != ProviderType.ANTHROPIC:
            config.provider_type = ProviderType.ANTHROPIC
        super().__init__(config)
    
    async def generate(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate content using Anthropic API"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        data = {
            "model": gen_config.model or self.config.model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": gen_config.max_tokens or self.config.max_tokens,
            "temperature": gen_config.temperature or self.config.temperature,
            "top_p": gen_config.top_p or self.config.top_p,
        }
        
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        try:
            response = await self.client.post(
                f"{self.config.base_url}/v1/messages",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            
            result = response.json()
            return result["completion"]
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def generate_stream(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming using Anthropic API"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        data = {
            "model": gen_config.model or self.config.model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": gen_config.max_tokens or self.config.max_tokens,
            "temperature": gen_config.temperature or self.config.temperature,
            "stream": True,
        }
        
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.config.base_url}/v1/messages",
                headers=headers,
                json=data,
            ) as response:
                async for line in response.aiter_lines():
                    if line and line.strip():
                        try:
                            chunk = json.loads(line)
                            if "completion" in chunk:
                                yield chunk["completion"]
                        except json.JSONDecodeError:
                            continue
                        
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise
    
    def _build_prompt(self, request: ContentRequest) -> str:
        """Build the prompt for Anthropic"""
        # Similar to OpenAI but formatted for Anthropic
        prompt_parts = []
        
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        if request.keywords:
            prompt_parts.append(f"Keywords: {', '.join(request.keywords)}")
        if request.platform:
            prompt_parts.append(f"Platform: {request.platform.value}")
        
        prompt_parts.append(f"Content type: {request.content_type.value}")
        
        if request.tone:
            prompt_parts.append(f"Tone: {request.tone.value}")
        if request.style:
            prompt_parts.append(f"Style: {request.style.value}")
        
        if request.min_length or request.max_length:
            constraints = []
            if request.min_length:
                constraints.append(f"min {request.min_length} chars")
            if request.max_length:
                constraints.append(f"max {request.max_length} chars")
            prompt_parts.append(f"Length: {', '.join(constraints)}")
        
        formatting = []
        if request.use_markdown:
            formatting.append("Markdown")
        if request.use_emojis:
            formatting.append("emojis")
        if request.use_hashtags:
            count = request.hashtag_count or "some"
            formatting.append(f"{count} hashtags")
        if formatting:
            prompt_parts.append(f"Format: {', '.join(formatting)}")
        
        if request.custom_instructions:
            prompt_parts.append(f"Instructions: {request.custom_instructions}")
        if request.target_audience:
            prompt_parts.append(f"Audience: {request.target_audience}")
        
        prompt_parts.append(f"Language: {request.language}")
        
        context = "\n".join(prompt_parts) if prompt_parts else ""

        return (
            f"Create {request.content_type.value} content for "
            f"{request.platform.value if request.platform else 'general use'}.\n"
            f"{context}\n\nPrompt: {request.prompt}"
        )


class GoogleProvider(AIProvider):
    """Google Generative AI provider"""
    
    def __init__(self, config: AIProviderConfig):
        if config.provider_type != ProviderType.GOOGLE:
            config.provider_type = ProviderType.GOOGLE
        super().__init__(config)
    
    async def generate(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate content using Google Generative AI"""
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed")
        
        genai.configure(api_key=self.config.api_key)
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        model = genai.GenerativeModel(
            model_name=gen_config.model or self.config.model,
        )
        
        try:
            response = await model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": gen_config.temperature or self.config.temperature,
                    "max_output_tokens": gen_config.max_tokens or self.config.max_tokens,
                    "top_p": gen_config.top_p or self.config.top_p,
                }
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Google generation failed: {e}")
            raise
    
    async def generate_stream(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming using Google API"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed")
        
        genai.configure(api_key=self.config.api_key)
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        model = genai.GenerativeModel(
            model_name=gen_config.model or self.config.model,
        )
        
        try:
            response = await model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": gen_config.temperature or self.config.temperature,
                    "max_output_tokens": gen_config.max_tokens or self.config.max_tokens,
                },
                stream=True,
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Google streaming failed: {e}")
            raise
    
    def _build_prompt(self, request: ContentRequest) -> str:
        """Build the prompt for Google"""
        # Similar structure to other providers
        prompt_parts = []
        
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        if request.keywords:
            prompt_parts.append(f"Keywords: {', '.join(request.keywords)}")
        if request.platform:
            prompt_parts.append(f"Platform: {request.platform.value}")
        
        prompt_parts.append(f"Content type: {request.content_type.value}")
        
        if request.tone:
            prompt_parts.append(f"Tone: {request.tone.value}")
        if request.style:
            prompt_parts.append(f"Style: {request.style.value}")
        
        if request.min_length or request.max_length:
            constraints = []
            if request.min_length:
                constraints.append(f"min {request.min_length} chars")
            if request.max_length:
                constraints.append(f"max {request.max_length} chars")
            prompt_parts.append(f"Length: {', '.join(constraints)}")
        
        formatting = []
        if request.use_markdown:
            formatting.append("Markdown")
        if request.use_emojis:
            formatting.append("emojis")
        if request.use_hashtags:
            count = request.hashtag_count or "some"
            formatting.append(f"{count} hashtags")
        if formatting:
            prompt_parts.append(f"Format: {', '.join(formatting)}")
        
        if request.custom_instructions:
            prompt_parts.append(f"Instructions: {request.custom_instructions}")
        if request.target_audience:
            prompt_parts.append(f"Audience: {request.target_audience}")
        
        prompt_parts.append(f"Language: {request.language}")
        
        context = "\n".join(prompt_parts) if prompt_parts else ""

        return (
            f"Create {request.content_type.value} content for "
            f"{request.platform.value if request.platform else 'general use'}.\n"
            f"{context}\n\nPrompt: {request.prompt}"
        )


class LocalProvider(AIProvider):
    """Local LLM provider using llama-cpp"""
    
    def __init__(self, config: AIProviderConfig):
        if config.provider_type != ProviderType.LOCAL:
            config.provider_type = ProviderType.LOCAL
        super().__init__(config)
        self._model = None
    
    def _initialize(self) -> None:
        """Initialize the local model"""
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError("llama-cpp-python package not installed")
        
        if not self.config.extra_config.get("model_path"):
            raise ValueError("Local model path not configured")
        
        self._model = Llama(
            model_path=self.config.extra_config["model_path"],
            n_ctx=self.config.max_tokens,
            n_threads=4,
        )
    
    async def generate(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate content using local LLM"""
        if not self._model:
            raise RuntimeError("Local model not loaded")
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        try:
            response = self._model(
                prompt,
                temperature=gen_config.temperature or self.config.temperature,
                max_tokens=gen_config.max_tokens or self.config.max_tokens,
                top_p=gen_config.top_p or self.config.top_p,
            )
            return response["choices"][0]["text"]
            
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            raise
    
    async def generate_stream(
        self,
        request: ContentRequest,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming using local LLM"""
        if not self._model:
            raise RuntimeError("Local model not loaded")
        
        prompt = self._build_prompt(request)
        gen_config = config or GenerationConfig()
        
        try:
            for chunk in self._model(
                prompt,
                temperature=gen_config.temperature or self.config.temperature,
                max_tokens=gen_config.max_tokens or self.config.max_tokens,
                top_p=gen_config.top_p or self.config.top_p,
                stream=True,
            ):
                yield chunk["choices"][0]["text"]
                
        except Exception as e:
            logger.error(f"Local streaming failed: {e}")
            raise
    
    def _build_prompt(self, request: ContentRequest) -> str:
        """Build the prompt for local LLM"""
        # Same structure as other providers
        prompt_parts = []
        
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        if request.keywords:
            prompt_parts.append(f"Keywords: {', '.join(request.keywords)}")
        if request.platform:
            prompt_parts.append(f"Platform: {request.platform.value}")
        
        prompt_parts.append(f"Content type: {request.content_type.value}")
        
        if request.tone:
            prompt_parts.append(f"Tone: {request.tone.value}")
        if request.style:
            prompt_parts.append(f"Style: {request.style.value}")
        
        if request.min_length or request.max_length:
            constraints = []
            if request.min_length:
                constraints.append(f"min {request.min_length} chars")
            if request.max_length:
                constraints.append(f"max {request.max_length} chars")
            prompt_parts.append(f"Length: {', '.join(constraints)}")
        
        formatting = []
        if request.use_markdown:
            formatting.append("Markdown")
        if request.use_emojis:
            formatting.append("emojis")
        if request.use_hashtags:
            count = request.hashtag_count or "some"
            formatting.append(f"{count} hashtags")
        if formatting:
            prompt_parts.append(f"Format: {', '.join(formatting)}")
        
        if request.custom_instructions:
            prompt_parts.append(f"Instructions: {request.custom_instructions}")
        if request.target_audience:
            prompt_parts.append(f"Audience: {request.target_audience}")
        
        prompt_parts.append(f"Language: {request.language}")
        
        context = "\n".join(prompt_parts) if prompt_parts else ""

        return (
            f"Create {request.content_type.value} content for "
            f"{request.platform.value if request.platform else 'general use'}.\n"
            f"{context}\n\nPrompt: {request.prompt}"
        )


class ProviderFactory:
    """Factory for creating AI providers"""
    
    _providers: Dict[str, AIProvider] = {}
    
    @classmethod
    def create_provider(
        cls,
        provider_type: Union[str, ProviderType],
        config: Optional[AIProviderConfig] = None
    ) -> AIProvider:
        """Create an AI provider instance"""
        provider_name = provider_type.value if isinstance(provider_type, ProviderType) else str(provider_type)
        custom_profile = web_configuration.get_provider(provider_name)

        if config is None:
            if custom_profile:
                config = AIProviderConfig.from_dict(custom_profile)
            else:
                provider_value = ProviderType(provider_name) if provider_name in {item.value for item in ProviderType} else ProviderType.OPENAI
                if provider_value == ProviderType.OPENAI:
                    config = AIProviderConfig(
                        provider_type=provider_value,
                        api_key=settings.ai.openai_api_key,
                        base_url=settings.ai.openai_base_url,
                        model=settings.ai.openai_model,
                    )
                elif provider_value == ProviderType.ANTHROPIC:
                    config = AIProviderConfig(
                        provider_type=provider_value,
                        api_key=settings.ai.anthropic_api_key,
                        base_url=settings.ai.anthropic_base_url,
                        model=settings.ai.anthropic_model,
                    )
                elif provider_value == ProviderType.GOOGLE:
                    config = AIProviderConfig(
                        provider_type=provider_value,
                        api_key=settings.ai.google_api_key,
                        model=settings.ai.google_model,
                    )
                elif provider_value == ProviderType.LOCAL:
                    config = AIProviderConfig(
                        provider_type=provider_value,
                        model=settings.ai.local_model_path or "llama-2-7b-chat",
                        extra_config={
                            "model_path": settings.ai.local_model_path
                        } if settings.ai.local_model_path else {},
                    )
                else:
                    raise ValueError(f"Unknown provider type: {provider_name}")

        if isinstance(provider_type, str):
            provider_type = ProviderType(custom_profile.get("provider_type", provider_name)) if custom_profile else ProviderType(provider_name)

        if provider_type == ProviderType.OPENAI:
            return OpenAIProvider(config)
        elif provider_type == ProviderType.ANTHROPIC:
            return AnthropicProvider(config)
        elif provider_type == ProviderType.GOOGLE:
            return GoogleProvider(config)
        elif provider_type == ProviderType.LOCAL:
            return LocalProvider(config)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @classmethod
    async def close_all(cls) -> None:
        """Close all provider connections"""
        for provider in cls._providers.values():
            await provider.close()
        cls._providers.clear()
