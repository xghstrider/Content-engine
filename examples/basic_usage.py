#!/usr/bin/env python3
"""
Basic usage examples for Content Engine
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from content_engine import ContentEngine
from content_engine.models.content import ContentType, ContentTone, PlatformType


async def basic_generation():
    """Basic content generation example"""
    print("=" * 60)
    print("BASIC CONTENT GENERATION")
    print("=" * 60)
    
    # Initialize the engine
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Example 1: Simple text generation
        print("\n1. Simple Text Generation:")
        response = await engine.generate(
            prompt="Write a short poem about AI and creativity",
            content_type="text",
        )
        print(f"Generated: {response.content[:200]}...")
        
        # Example 2: Twitter content
        print("\n2. Twitter Content:")
        tweet = await engine.generate(
            prompt="Announcing our new AI content engine!",
            platform="twitter",
            content_type="social_post",
            tone="excited",
            use_emojis=True,
            use_hashtags=True,
        )
        print(f"Tweet: {tweet.content}")
        
        # Example 3: Blog post
        print("\n3. Blog Post:")
        blog = await engine.generate(
            prompt="The future of AI in content creation",
            platform="web",
            content_type="blog_post",
            tone="professional",
            min_length=500,
            use_markdown=True,
        )
        print(f"Blog post (first 200 chars): {blog.content[:200]}...")
        
        # Example 4: Email content
        print("\n4. Email Content:")
        email = await engine.generate(
            prompt="Welcome to our new AI content platform",
            platform="email",
            content_type="email",
            tone="friendly",
        )
        print(f"Email: {email.content[:200]}...")
        
    finally:
        await engine.close()


async def platform_specific():
    """Platform-specific generation examples"""
    print("\n" + "=" * 60)
    print("PLATFORM-SPECIFIC GENERATION")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Twitter
        print("\n1. Twitter:")
        tweet = await engine.generate_twitter(
            "Check out our new AI-powered content engine! 🚀",
            use_emojis=True,
            use_hashtags=True,
            hashtag_count=3,
        )
        print(f"Tweet: {tweet.content}")
        
        # Facebook
        print("\n2. Facebook:")
        fb = await engine.generate_facebook(
            "Announcing our new AI content engine that can generate content for all social media platforms!",
            use_emojis=True,
            use_hashtags=True,
        )
        print(f"Facebook post: {fb.content[:200]}...")
        
        # Instagram
        print("\n3. Instagram:")
        ig = await engine.generate_instagram(
            "Beautiful sunset at the beach with our new AI content engine",
            use_emojis=True,
            use_hashtags=True,
        )
        print(f"Instagram caption: {ig.content}")
        
        # LinkedIn
        print("\n4. LinkedIn:")
        li = await engine.generate_linkedin(
            "The future of AI in professional content creation",
            tone="professional",
        )
        print(f"LinkedIn post: {li.content[:200]}...")
        
        # Pinterest
        print("\n5. Pinterest:")
        pin = await engine.generate_pinterest(
            "DIY home decor ideas using AI-generated designs",
            use_emojis=True,
        )
        print(f"Pinterest description: {pin.content}")
        
        # Snapchat
        print("\n6. Snapchat:")
        snap = await engine.generate_snapchat(
            "Having fun with our new AI content engine!",
            use_emojis=True,
        )
        print(f"Snapchat story: {snap.content}")
        
        # Website
        print("\n7. Website:")
        web = await engine.generate_website(
            "The ultimate guide to AI-powered content creation",
            content_type="blog_post",
        )
        print(f"Website content: {web.content[:200]}...")
        
        # Email
        print("\n8. Email:")
        email = await engine.generate_email(
            "Welcome to our AI content platform",
            tone="friendly",
        )
        print(f"Email: {email.content[:200]}...")
        
    finally:
        await engine.close()


async def advanced_features():
    """Advanced features examples"""
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Batch generation
        print("\n1. Batch Generation:")
        prompts = [
            "Top 5 AI tools for social media",
            "How to create engaging content with AI",
            "The future of AI in marketing",
        ]
        responses = await engine.generate_batch(prompts, platform="twitter")
        for i, resp in enumerate(responses, 1):
            print(f"  {i}. {resp.content[:100]}...")
        
        # Alternatives
        print("\n2. Generate Alternatives:")
        alternatives = await engine.create_alternatives(
            "AI is transforming content creation",
            count=3,
            platform="twitter",
        )
        for i, alt in enumerate(alternatives, 1):
            print(f"  Alternative {i}: {alt.content}")
        
        # Regeneration
        print("\n3. Regenerate Content:")
        original = await engine.generate(
            "The benefits of AI in content creation",
            platform="twitter",
        )
        print(f"  Original: {original.content}")
        
        regenerated = await engine.regenerate(original)
        print(f"  Regenerated: {regenerated.content}")
        
        # Content analysis
        print("\n4. Content Analysis:")
        analysis = await engine.analyze_content(
            "AI is revolutionizing the way we create content. It's amazing!"
        )
        print(f"  Sentiment: {analysis.get('sentiment', 'N/A')}")
        print(f"  Tone: {analysis.get('tone', 'N/A')}")
        print(f"  Keywords: {analysis.get('keywords', [])}")
        
    finally:
        await engine.close()


async def customization():
    """Customization examples"""
    print("\n" + "=" * 60)
    print("CUSTOMIZATION OPTIONS")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        # Different tones
        print("\n1. Different Tones:")
        tones = ["professional", "casual", "humorous", "inspirational"]
        for tone in tones:
            resp = await engine.generate(
                "AI is changing the world",
                tone=tone,
                platform="twitter",
            )
            print(f"  {tone.capitalize()}: {resp.content}")
        
        # Different styles
        print("\n2. Different Styles:")
        styles = ["concise", "detailed", "creative"]
        for style in styles:
            resp = await engine.generate(
                "The impact of AI on content creation",
                style=style,
                platform="linkedin",
            )
            print(f"  {style.capitalize()}: {resp.content[:100]}...")
        
        # Length control
        print("\n3. Length Control:")
        for max_len in [50, 100, 200]:
            resp = await engine.generate(
                "AI is transforming content creation",
                max_length=max_len,
                platform="twitter",
            )
            print(f"  Max {max_len} chars: {resp.content} (actual: {len(resp.content)})")
        
        # Formatting options
        print("\n4. Formatting Options:")
        resp = await engine.generate(
            "AI content generation is amazing",
            platform="twitter",
            use_emojis=True,
            use_hashtags=True,
            hashtag_count=3,
        )
        print(f"  With emojis and hashtags: {resp.content}")
        
    finally:
        await engine.close()


async def main():
    """Run all examples"""
    print("CONTENT ENGINE - BASIC USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        await basic_generation()
        await platform_specific()
        await advanced_features()
        await customization()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
