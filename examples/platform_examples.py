#!/usr/bin/env python3
"""
Platform-specific examples for Content Engine
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


async def twitter_examples():
    """Twitter-specific examples"""
    print("=" * 60)
    print("TWITTER EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = TwitterGenerator(engine)
        
        # Example 1: Basic tweet
        print("\n1. Basic Tweet:")
        tweet = await generator.generate(
            "Just launched our new AI content engine! 🚀",
            use_emojis=True,
            use_hashtags=True,
        )
        print(f"   {tweet.content}")
        
        # Example 2: Thread generation
        print("\n2. Twitter Thread (3 tweets):")
        thread = await generator.generate_thread(
            "Introduction to AI in content creation",
            tweet_count=3,
        )
        for i, tweet in enumerate(thread, 1):
            print(f"   Tweet {i}: {tweet.content}")
        
        # Example 3: Reply generation
        print("\n3. Reply to Tweet:")
        reply = await generator.generate_reply(
            original_tweet="AI is changing the world of content creation!",
            reply_style="engaging",
        )
        print(f"   {reply.content}")
        
        # Example 4: Quote tweet
        print("\n4. Quote Tweet:")
        quote = await generator.generate_quote_tweet(
            original_tweet="AI is the future of content creation",
            quote_text="And it's here today!",
        )
        print(f"   {quote.content}")
        
        # Example 5: Content validation
        print("\n5. Content Validation:")
        test_content = "This is a test tweet that is way too long and exceeds the character limit for Twitter which is 280 characters and this one is definitely longer than that"
        validation = generator.validate_content(test_content)
        print(f"   Valid: {validation['is_valid']}")
        print(f"   Character count: {validation['character_count']}")
        print(f"   Max length: {validation['max_length']}")
        
    finally:
        await engine.close()


async def facebook_examples():
    """Facebook-specific examples"""
    print("\n" + "=" * 60)
    print("FACEBOOK EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = FacebookGenerator(engine)
        
        # Example 1: Basic post
        print("\n1. Basic Post:")
        post = await generator.generate(
            "Announcing our new AI content engine that can generate content for all social media platforms!",
            use_emojis=True,
            use_hashtags=True,
        )
        print(f"   {post.content[:200]}...")
        
        # Example 2: Album post
        print("\n2. Album Post:")
        album = await generator.generate_album_post(
            images=["image1.jpg", "image2.jpg", "image3.jpg"],
            caption="Our team at the recent AI conference",
        )
        print(f"   {album.content}")
        
        # Example 3: Video post
        print("\n3. Video Post:")
        video = await generator.generate_video_post(
            video_url="https://example.com/video.mp4",
            description="Our new AI content engine in action",
        )
        print(f"   {video.content}")
        
        # Example 4: Link post
        print("\n4. Link Post:")
        link = await generator.generate_link_post(
            link_url="https://example.com",
            link_title="Content Engine - AI Powered Content Creation",
            link_description="Generate content for all platforms with AI",
        )
        print(f"   {link.content}")
        
        # Example 5: Event post
        print("\n5. Event Post:")
        event = await generator.generate_event_post(
            event_name="AI Content Creation Workshop",
            event_date="2024-12-15",
            event_location="San Francisco, CA",
            event_description="Learn how to use AI for content creation",
        )
        print(f"   {event.content[:200]}...")
        
    finally:
        await engine.close()


async def instagram_examples():
    """Instagram-specific examples"""
    print("\n" + "=" * 60)
    print("INSTAGRAM EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = InstagramGenerator(engine)
        
        # Example 1: Caption generation
        print("\n1. Caption Generation:")
        caption = await generator.generate_caption(
            image_description="A beautiful sunset over the ocean with a sailboat",
        )
        print(f"   {caption.content}")
        
        # Example 2: Carousel caption
        print("\n2. Carousel Caption:")
        carousel = await generator.generate_carousel_caption(
            image_descriptions=[
                "First image showing our product",
                "Second image with features",
                "Third image with pricing",
            ],
        )
        print(f"   {carousel.content}")
        
        # Example 3: Story content
        print("\n3. Story Content:")
        story = await generator.generate_story_content(
            image_video_description="Behind the scenes of our new AI content engine",
        )
        print(f"   {story.content}")
        
        # Example 4: Reel description
        print("\n4. Reel Description:")
        reel = await generator.generate_reel_description(
            video_description="Tutorial on how to use our AI content engine",
        )
        print(f"   {reel.content}")
        
        # Example 5: Hashtag generation
        print("\n5. Hashtag Generation:")
        hashtags = await generator.generate_hashtag_set(
            topic="AI content creation",
            count=10,
        )
        print(f"   {', '.join(hashtags)}")
        
        # Example 6: Alt text generation
        print("\n6. Alt Text Generation:")
        alt_text = await generator.generate_alt_text(
            image_description="A group of people working together on laptops in a modern office",
        )
        print(f"   {alt_text}")
        
    finally:
        await engine.close()


async def linkedin_examples():
    """LinkedIn-specific examples"""
    print("\n" + "=" * 60)
    print("LINKEDIN EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = LinkedInGenerator(engine)
        
        # Example 1: Basic post
        print("\n1. Basic Post:")
        post = await generator.generate(
            "The future of AI in professional content creation",
            tone="professional",
        )
        print(f"   {post.content[:200]}...")
        
        # Example 2: Article generation
        print("\n2. Article Generation:")
        article = await generator.generate_article(
            title="The Impact of AI on Content Creation",
            outline=[
                "Introduction to AI in content creation",
                "Benefits of AI-powered content",
                "Challenges and considerations",
                "The future of AI in content",
            ],
        )
        print(f"   {article.content[:300]}...")
        
        # Example 3: Company update
        print("\n3. Company Update:")
        update = await generator.generate_company_update(
            company_name="Content Engine Inc.",
            update_type="Product Launch",
            details="We're excited to announce our new AI content generation platform",
        )
        print(f"   {update.content}")
        
        # Example 4: Job posting
        print("\n4. Job Posting:")
        job = await generator.generate_job_posting(
            position="AI Content Specialist",
            company="Content Engine Inc.",
            description="Create AI-generated content for various platforms",
            requirements=[
                "Experience with AI tools",
                "Strong writing skills",
                "Knowledge of social media platforms",
            ],
        )
        print(f"   {job.content[:300]}...")
        
        # Example 5: Achievement post
        print("\n5. Achievement Post:")
        achievement = await generator.generate_achievement_post(
            achievement="Launched our AI content engine to 10,000 users",
            impact="Revolutionizing content creation for businesses worldwide",
        )
        print(f"   {achievement.content}")
        
    finally:
        await engine.close()


async def pinterest_examples():
    """Pinterest-specific examples"""
    print("\n" + "=" * 60)
    print("PINTEREST EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = PinterestGenerator(engine)
        
        # Example 1: Pin description
        print("\n1. Pin Description:")
        pin = await generator.generate_pin_description(
            image_url="https://example.com/image.jpg",
            image_description="DIY home decor with AI-generated designs",
            link_url="https://example.com",
        )
        print(f"   {pin.content}")
        
        # Example 2: Board description
        print("\n2. Board Description:")
        board = await generator.generate_board_description(
            board_name="AI Content Creation",
            board_topic="Tips and ideas for using AI in content creation",
        )
        print(f"   {board.content}")
        
        # Example 3: SEO description
        print("\n3. SEO Description:")
        seo = await generator.generate_seo_description(
            product_name="AI Content Engine",
            product_features=[
                "Multi-platform support",
                "AI-powered generation",
                "Customizable content",
                "Batch processing",
            ],
        )
        print(f"   {seo.content}")
        
        # Example 4: Recipe pin
        print("\n4. Recipe Pin:")
        recipe = await generator.generate_recipe_pin(
            recipe_name="AI-Generated Chocolate Cake",
            ingredients=[
                "2 cups flour",
                "1 cup sugar",
                "3 eggs",
                "1 cup chocolate",
            ],
            instructions=[
                "Mix all ingredients together",
                "Bake at 350°F for 30 minutes",
                "Let cool and enjoy",
            ],
        )
        print(f"   {recipe.content[:300]}...")
        
    finally:
        await engine.close()


async def snapchat_examples():
    """Snapchat-specific examples"""
    print("\n" + "=" * 60)
    print("SNAPCHAT EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = SnapchatGenerator(engine)
        
        # Example 1: Story content
        print("\n1. Story Content:")
        story = await generator.generate_story(
            image_video_description="Having fun with our new AI content engine",
        )
        print(f"   {story.content}")
        
        # Example 2: Spotlight content
        print("\n2. Spotlight Content:")
        spotlight = await generator.generate_spotlight_content(
            video_description="Tutorial on using our AI content engine",
        )
        print(f"   {spotlight.content}")
        
        # Example 3: Filter content
        print("\n3. Filter Content:")
        filter_content = await generator.generate_filter_content(
            filter_name="AI Power",
            filter_description="Transforms your face with AI-powered effects",
        )
        print(f"   {filter_content.content}")
        
        # Example 4: Geofilter content
        print("\n4. Geofilter Content:")
        geo = await generator.generate_geofilter_content(
            location="San Francisco",
            event="AI Conference 2024",
        )
        print(f"   {geo.content}")
        
    finally:
        await engine.close()


async def website_examples():
    """Website-specific examples"""
    print("\n" + "=" * 60)
    print("WEBSITE EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = WebsiteGenerator(engine)
        
        # Example 1: Blog post
        print("\n1. Blog Post:")
        blog = await generator.generate_blog_post(
            title="The Ultimate Guide to AI-Powered Content Creation",
            outline=[
                "Introduction to AI in content creation",
                "Benefits of using AI for content",
                "How to get started with AI content tools",
                "Best practices and tips",
                "The future of AI and content",
            ],
        )
        print(f"   {blog.content[:300]}...")
        
        # Example 2: Website page
        print("\n2. Website Page:")
        page = await generator.generate_website_page(
            page_title="About Content Engine",
            sections=[
                "Our Story",
                "Our Team",
                "Our Mission",
                "Contact Us",
            ],
        )
        print(f"   {page.content[:300]}...")
        
        # Example 3: Product description
        print("\n3. Product Description:")
        product = await generator.generate_product_description(
            product_name="AI Content Engine Pro",
            features=[
                "Multi-platform support",
                "AI-powered generation",
                "Customizable content",
                "Batch processing",
                "24/7 support",
            ],
            benefits=[
                "Save time on content creation",
                "Increase engagement",
                "Improve content quality",
                "Scale content production",
            ],
        )
        print(f"   {product.content[:300]}...")
        
        # Example 4: SEO content
        print("\n4. SEO Content:")
        seo = await generator.generate_seo_content(
            keyword="AI content generation",
            related_keywords=[
                "AI content tools",
                "automated content creation",
                "AI writing assistant",
                "content generation software",
            ],
        )
        print(f"   {seo.content[:300]}...")
        
        # Example 5: Landing page
        print("\n5. Landing Page:")
        landing = await generator.generate_landing_page(
            product_service="AI Content Engine",
            value_proposition="Generate high-quality content for all platforms with AI",
            features=[
                "Multi-platform support",
                "AI-powered generation",
                "Customizable content",
                "Batch processing",
            ],
        )
        print(f"   {landing.content[:300]}...")
        
    finally:
        await engine.close()


async def email_examples():
    """Email-specific examples"""
    print("\n" + "=" * 60)
    print("EMAIL EXAMPLES")
    print("=" * 60)
    
    engine = ContentEngine()
    await engine.initialize()
    
    try:
        generator = EmailGenerator(engine)
        
        # Example 1: Basic email
        print("\n1. Basic Email:")
        email = await generator.generate_email(
            subject="Welcome to Content Engine",
            body_prompt="Welcome our new user to the platform",
            recipient="john@example.com",
        )
        print(f"   Subject: {email.metadata.get('subject', 'N/A')}")
        print(f"   Body: {email.content[:200]}...")
        
        # Example 2: Subject line
        print("\n2. Subject Line:")
        subject = await generator.generate_subject_line(
            email_purpose="Promote our new AI content engine",
        )
        print(f"   {subject.content}")
        
        # Example 3: Email body
        print("\n3. Email Body:")
        body = await generator.generate_email_body(
            purpose="Introduce new features",
            key_points=[
                "New AI models available",
                "Improved generation speed",
                "Enhanced customization options",
            ],
            call_to_action="Try the new features today!",
        )
        print(f"   {body.content[:300]}...")
        
        # Example 4: Newsletter
        print("\n4. Newsletter:")
        newsletter = await generator.generate_newsletter(
            title="Content Engine Monthly Newsletter",
            articles=[
                "New AI models released",
                "Product updates and improvements",
                "Customer success stories",
            ],
        )
        print(f"   {newsletter.content[:300]}...")
        
        # Example 5: Promotional email
        print("\n5. Promotional Email:")
        promo = await generator.generate_promotional_email(
            product_service="AI Content Engine Pro",
            offer="20% off for the first month",
            deadline="2024-12-31",
        )
        print(f"   {promo.content[:300]}...")
        
    finally:
        await engine.close()


async def main():
    """Run all platform examples"""
    print("CONTENT ENGINE - PLATFORM-SPECIFIC EXAMPLES")
    print("=" * 60)
    
    try:
        await twitter_examples()
        await facebook_examples()
        await instagram_examples()
        await linkedin_examples()
        await pinterest_examples()
        await snapchat_examples()
        await website_examples()
        await email_examples()
        
        print("\n" + "=" * 60)
        print("ALL PLATFORM EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
