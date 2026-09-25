#!/usr/bin/env python3
"""
Advanced usage examples for Content Engine
"""

import asyncio
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from content_engine import ContentEngine
from content_engine.config.settings import get_settings
from content_engine.core.cache import ContentCache
from content_engine.models.content import ContentRequest, ContentResponse, ContentType, ContentTone
from content_engine.models.generation import GenerationConfig
from content_engine.templates.manager import TemplateManager
from content_engine.templates.library import TemplateLibrary


async def caching_examples():
    """Caching examples"""
    print("=" * 60)
    print("CACHING EXAMPLES")
    print("=" * 60)
    
    # Create a custom cache
    cache = ContentCache()
    
    engine = ContentEngine(cache=cache)
    await engine.initialize()
    
    try:
        # Example 1: Generate and cache content
        print("\n1. Generate and Cache Content:")
        request = ContentRequest(
            prompt="AI is transforming content creation",
            platform="twitter",
        )
        
        response1 = await engine.generate_advanced(request)
        print(f"   First generation: {response1.content}")
        print(f"   Request ID: {response1.request_id}")
        
        # Example 2: Retrieve from cache
        print("\n2. Retrieve from Cache:")
        response2 = await engine.generate_advanced(request)
        print(f"   Second generation: {response2.content}")
        print(f"   Request ID: {response2.request_id}")
        print(f"   Same content: {response1.content == response2.content}")
        
        # Example 3: Cache statistics
        print("\n3. Cache Statistics:")
        stats = await cache.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Example 4: Clear cache
        print("\n4. Clear Cache:")
        count = await cache.clear()
        print(f"   Cleared {count} items")
        
        stats = await cache.get_stats()
        print(f"   Items after clear: {stats['total_items']}")
        
    finally:
        await engine.close()


async def configuration_examples():
    """Configuration examples"""
    print("\n" + "=" * 60)
    print("CONFIGURATION EXAMPLES")
    print("=" * 60)
    
    # Get settings
    settings = get_settings()
    
    print("\n1. Current Settings:")
    print(f"   App Name: {settings.app_name}")
    print(f"   App Version: {settings.app_version}")
    print(f"   Debug Mode: {settings.debug}")
    print(f"   Default Provider: {settings.ai.default_provider}")
    
    print("\n2. Platform Settings:")
    print(f"   Twitter Max Length: {settings.platforms.twitter_max_length}")
    print(f"   Facebook Post Length: {settings.platforms.facebook_post_length}")
    print(f"   Instagram Caption Length: {settings.platforms.instagram_caption_length}")
    print(f"   LinkedIn Post Length: {settings.platforms.linkedin_post_length}")
    
    print("\n3. Cache Settings:")
    print(f"   Cache Enabled: {settings.cache.cache_enabled}")
    print(f"   Cache TTL: {settings.cache.cache_ttl}")
    print(f"   Max Cache Size: {settings.cache.max_cache_size}")


async def generation_config_examples():
    """Generation configuration examples"""
    print("\n" + "=" * 60)
    print("GENERATION CONFIGURATION EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Example 1: Custom generation config
        print("\n1. Custom Generation Config:")
        config = GenerationConfig(
            provider="openai",
            model="gpt-4-turbo-preview",
            temperature=0.8,
            max_tokens=2000,
            top_p=0.9,
            use_cache=False,
            max_retries=2,
        )
        
        request = ContentRequest(
            prompt="Write a creative story about AI and content creation",
            content_type="story",
        )
        
        response = await engine.generate_advanced(request, config)
        print(f"   Generated with custom config: {response.content[:200]}...")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        
        # Example 2: Streaming generation
        print("\n2. Streaming Generation:")
        print("   ", end="")
        async for chunk in engine.generate_stream(
            "Write a poem about AI",
            platform="twitter",
        ):
            print(chunk, end="", flush=True)
        print()
        
        # Example 3: Batch generation with config
        print("\n3. Batch Generation with Config:")
        prompts = [
            "AI in content creation",
            "The future of AI",
            "AI tools for marketers",
        ]
        
        config = GenerationConfig(
            temperature=0.7,
            max_tokens=1000,
        )
        
        requests = [ContentRequest(prompt=p, platform="twitter") for p in prompts]
        responses = await engine.generator.generate_batch(requests, config)
        
        for i, resp in enumerate(responses, 1):
            print(f"   {i}. {resp.content}")
        
    finally:
        await engine.close()


async def template_examples():
    """Template examples"""
    print("\n" + "=" * 60)
    print("TEMPLATE EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Initialize template manager
        template_manager = TemplateManager()
        await template_manager.initialize()
        
        # Example 1: List templates
        print("\n1. List Available Templates:")
        templates = await template_manager.list_templates()
        print(f"   Found {len(templates)} templates")
        for i, template in enumerate(templates[:5], 1):
            print(f"   {i}. {template.name} ({template.id})")
        
        # Example 2: Get specific template
        print("\n2. Get Specific Template:")
        template = await template_manager.get_template("twitter_basic")
        if template:
            print(f"   Name: {template.name}")
            print(f"   Description: {template.description}")
            print(f"   Content: {template.content[:100]}...")
        
        # Example 3: Render template
        print("\n3. Render Template:")
        variables = {
            "prompt": "Check out our new AI content engine!",
            "hashtags": "#AI #Content #Innovation",
        }
        rendered = await template_manager.render_template("twitter_basic", variables)
        print(f"   Rendered: {rendered}")
        
        # Example 4: Search templates
        print("\n4. Search Templates:")
        results = await template_manager.search_templates("twitter", limit=3)
        for i, template in enumerate(results, 1):
            print(f"   {i}. {template.name} ({template.id})")
        
        # Example 5: Create custom template
        print("\n5. Create Custom Template:")
        from content_engine.models.templates import Template, TemplateVariable, TemplateType, TemplateCategory
        
        custom_template = Template(
            id="custom_tweet",
            name="Custom Tweet",
            description="My custom tweet template",
            template_type=TemplateType.TEXT,
            category=TemplateCategory.SOCIAL_MEDIA,
            content="{emoji} {message} {hashtags}",
            variables=[
                TemplateVariable(
                    name="emoji",
                    description="Emoji to use",
                    default_value="🚀",
                ),
                TemplateVariable(
                    name="message",
                    description="Main message",
                    required=True,
                ),
                TemplateVariable(
                    name="hashtags",
                    description="Hashtags to include",
                    default_value="",
                ),
            ],
            platform="twitter",
        )
        
        created = await template_manager.create_template(custom_template)
        print(f"   Created template: {created.id}")
        
        # Example 6: Render custom template
        print("\n6. Render Custom Template:")
        rendered = await template_manager.render_template(
            "custom_tweet",
            {
                "emoji": "🎉",
                "message": "Our new template system is live!",
                "hashtags": "#Templates #AI",
            }
        )
        print(f"   Rendered: {rendered}")
        
    finally:
        await engine.close()


async def analysis_examples():
    """Content analysis examples"""
    print("\n" + "=" * 60)
    print("CONTENT ANALYSIS EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Example 1: Analyze text content
        print("\n1. Analyze Text Content:")
        content = """
        AI is revolutionizing the way we create content. 
        It's making content creation faster, more efficient, and more creative.
        With AI, anyone can create high-quality content for any platform.
        """
        
        analysis = await engine.analyze_content(content)
        print(f"   Sentiment: {analysis.get('sentiment', 'N/A')}")
        print(f"   Tone: {analysis.get('tone', 'N/A')}")
        print(f"   Keywords: {analysis.get('keywords', [])}")
        print(f"   Readability Score: {analysis.get('readability_score', 0)}")
        print(f"   Quality Score: {analysis.get('quality_score', 0)}")
        
        # Example 2: Analyze with platform context
        print("\n2. Analyze with Platform Context:")
        request = ContentRequest(
            prompt="AI content generation",
            platform="twitter",
        )
        analysis = await engine.generator.provider.analyze(content, request)
        print(f"   Platform-specific analysis: {analysis}")
        
        # Example 3: Validate content for platform
        print("\n3. Validate Content for Platform:")
        from content_engine.platforms import TwitterGenerator
        
        twitter_gen = TwitterGenerator(engine)
        validation = twitter_gen.validate_content(
            "This is a test tweet that is way too long and exceeds the character limit for Twitter which is 280 characters and this one is definitely longer than that"
        )
        print(f"   Valid: {validation['is_valid']}")
        print(f"   Character Count: {validation['character_count']}")
        print(f"   Max Length: {validation['max_length']}")
        print(f"   Errors: {validation['errors']}")
        
    finally:
        await engine.close()


async def provider_examples():
    """Provider management examples"""
    print("\n" + "=" * 60)
    print("PROVIDER MANAGEMENT EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Example 1: Get current provider
        print("\n1. Current Provider:")
        info = await engine.get_provider_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Example 2: List available providers
        print("\n2. Available Providers:")
        from content_engine.config.providers import DEFAULT_PROVIDERS
        for provider in DEFAULT_PROVIDERS.keys():
            print(f"   - {provider}")
        
        # Example 3: Change provider (if configured)
        print("\n3. Change Provider:")
        try:
            # Try to change to anthropic (if API key is configured)
            await engine.change_provider("anthropic")
            info = await engine.get_provider_info()
            print(f"   Changed to: {info['provider']}")
        except Exception as e:
            print(f"   Could not change provider: {e}")
        
        # Example 4: Provider-specific configuration
        print("\n4. Provider-Specific Configuration:")
        from content_engine.models.generation import GenerationConfig
        
        config = GenerationConfig(
            provider="openai",
            model="gpt-4-turbo-preview",
            temperature=0.9,
            max_tokens=4096,
        )
        
        print(f"   Provider: {config.provider}")
        print(f"   Model: {config.model}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Max Tokens: {config.max_tokens}")
        
    finally:
        await engine.close()


async def error_handling_examples():
    """Error handling examples"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Example 1: Handle invalid request
        print("\n1. Invalid Request Handling:")
        try:
            request = ContentRequest(
                prompt="",  # Empty prompt
                platform="twitter",
                min_length=1000,  # Too long for Twitter
            )
            response = await engine.generate_advanced(request)
        except Exception as e:
            print(f"   Caught error: {type(e).__name__}: {e}")
        
        # Example 2: Handle content validation
        print("\n2. Content Validation:")
        try:
            request = ContentRequest(
                prompt="A",
                platform="twitter",
                min_length=100,  # Request longer content than possible
            )
            response = await engine.generate_advanced(request)
            print(f"   Generated: {response.content}")
        except Exception as e:
            print(f"   Validation error: {e}")
        
        # Example 3: Handle missing API key
        print("\n3. Missing API Key:")
        try:
            # Try to use a provider without API key
            await engine.change_provider("anthropic")
            response = await engine.generate(
                "Test",
                provider="anthropic",
            )
        except Exception as e:
            print(f"   Provider error: {type(e).__name__}: {e}")
        
    finally:
        await engine.close()


async def main():
    """Run all advanced examples"""
    print("CONTENT ENGINE - ADVANCED USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        await caching_examples()
        await configuration_examples()
        await generation_config_examples()
        await template_examples()
        await analysis_examples()
        await provider_examples()
        await error_handling_examples()
        
        print("\n" + "=" * 60)
        print("ALL ADVANCED EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
