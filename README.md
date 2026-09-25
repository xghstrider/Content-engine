# Content Engine - AI Powered Content Creation Platform

![Content Engine Logo](https://img.shields.io/badge/Content%20Engine-AI%20Powered-blueviolet)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Content Engine** is a comprehensive AI-powered content generation platform designed for creating and customizing all types of content, especially for social media platforms and websites.

## Features

### 🚀 Core Capabilities

- **Multi-Platform Support**: Generate content for Twitter/X, Facebook, Instagram, LinkedIn, Pinterest, Snapchat, and more
- **Multiple AI Providers**: Support for OpenAI, Anthropic, Google Generative AI, and local LLMs
- **Customizable Content**: Control tone, style, length, formatting, and more
- **Batch Processing**: Generate content for multiple prompts simultaneously
- **Streaming Generation**: Real-time content generation with streaming
- **Content Analysis**: Analyze existing content for sentiment, tone, keywords, and more
- **Caching**: Intelligent caching for faster repeated requests

### 📱 Platform-Specific Features

#### Twitter/X
- Tweet generation with character limits
- Thread creation (multiple connected tweets)
- Reply and quote tweet generation
- Hashtag optimization
- Engagement predictions

#### Facebook
- Post generation with various formats
- Album post creation
- Video post optimization
- Link post generation
- Event announcements

#### Instagram
- Caption generation
- Carousel post support
- Story content creation
- Reel descriptions
- Hashtag strategy
- Alt text generation

#### LinkedIn
- Professional post generation
- Article creation
- Company updates
- Job posting generation
- Industry insights

#### Pinterest
- Pin description generation
- Board descriptions
- SEO-optimized content
- Recipe and DIY pin generation

#### Snapchat
- Story content generation
- Spotlight content optimization
- Filter/lens promotion
- Geofilter content

#### Website/Blog
- Blog post generation
- Website page creation
- Product descriptions
- SEO-optimized content
- Landing pages

#### Email
- Email content generation
- Subject line optimization
- Newsletter creation
- Promotional emails
- Follow-up emails

### 🎨 Customization Options

- **Content Types**: Text, social posts, blog posts, emails, ad copy, product descriptions, SEO content, and more
- **Tones**: Professional, casual, friendly, formal, humorous, sarcastic, inspirational, educational, promotional, storytelling, conversational, technical, persuasive, emotional
- **Styles**: Short, medium, long, concise, detailed, simple, complex, creative, direct, metaphorical
- **Quality Levels**: Draft, standard, premium, professional
- **Formatting**: Markdown, emojis, hashtags, line breaks
- **Length Control**: Minimum and maximum character/word counts

### 🤖 AI Provider Support

- **OpenAI**: GPT-4, GPT-3.5, and other models
- **Anthropic**: Claude 3 models
- **Google**: Gemini models
- **Local LLMs**: Support for local models via llama-cpp

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/xghstrider/Content-engine.git
cd Content-engine

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Install optional dependencies for local LLM support
pip install -e ".[local-llm]"
```

### Environment Configuration

Create a `.env` file in the project root with your API keys:

```env
# Application settings
APP_NAME=Content Engine
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# AI Provider settings
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=https://api.openai.com/v1

ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL=gemini-1.5-pro

# Default provider (openai, anthropic, google, local)
DEFAULT_PROVIDER=openai

# Platform settings
TWITTER_MAX_LENGTH=280
FACEBOOK_POST_LENGTH=63206
INSTAGRAM_CAPTION_LENGTH=2200
LINKEDIN_POST_LENGTH=3000

# Cache settings
CACHE_ENABLED=True
CACHE_TTL=3600
MAX_CACHE_SIZE=1000
```

## Usage

### As a Python Library

```python
import asyncio
from content_engine import ContentEngine

async def main():
    # Initialize the engine
    engine = ContentEngine()
    await engine.initialize()
    
    # Generate Twitter content
    response = await engine.generate_twitter(
        "Check out our new AI-powered content engine! 🚀",
        tone="excited",
        use_emojis=True,
        use_hashtags=True,
    )
    print(response.content)
    
    # Generate a blog post
    blog = await engine.generate_website(
        "The future of AI in content creation",
        content_type="blog_post",
        tone="professional",
        min_length=1000,
    )
    print(blog.content)
    
    # Generate multiple alternatives
    alternatives = await engine.create_alternatives(
        "Top 10 AI tools for developers",
        count=3,
        platform="twitter",
    )
    for alt in alternatives:
        print(alt.content)
    
    # Close the engine
    await engine.close()

asyncio.run(main())
```

### Using the CLI

```bash
# Initialize the engine
content-engine init

# Generate content
content-engine generate "Create a tweet about AI in content creation" --platform twitter --tone excited

# Generate multiple alternatives
content-engine alternatives "Top AI tools for developers" --count 5

# Generate Twitter thread
content-engine platform twitter "Introduction to AI content generation" --thread --tweet-count 5

# List available platforms
content-engine platforms

# Change AI provider
content-engine provider anthropic

# Show system info
content-engine info

# Manage cache
content-engine cache --stats
content-engine cache --clear

# Start interactive shell
content-engine shell
```

### Using the API Server

```bash
# Start the API server
content-engine

# Or explicitly
python -m content_engine.api.server
```

Then make requests to the API:

```bash
# Generate content
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a tweet about AI content generation",
    "platform": "twitter",
    "tone": "excited",
    "use_emojis": true,
    "use_hashtags": true
  }'

# Generate Twitter content
curl -X POST http://localhost:8000/api/v1/content/twitter \
  -H "Content-Type: application/json" \
  -d '{"prompt": "AI is transforming content creation"}'

# List templates
curl http://localhost:8000/api/v1/templates

# Get health status
curl http://localhost:8000/health
```

### API Endpoints

#### Content Generation
- `POST /api/v1/content/generate` - Generate content from a request
- `POST /api/v1/content/generate_batch` - Generate content for multiple requests
- `POST /api/v1/content/stream` - Generate content with streaming
- `POST /api/v1/content/regenerate` - Regenerate content with variations
- `POST /api/v1/content/alternatives` - Create multiple alternatives
- `POST /api/v1/content/analyze` - Analyze existing content

#### Platform-Specific
- `POST /api/v1/platforms/twitter` - Generate Twitter/X content
- `POST /api/v1/platforms/facebook` - Generate Facebook content
- `POST /api/v1/platforms/instagram` - Generate Instagram content
- `POST /api/v1/platforms/linkedin` - Generate LinkedIn content
- `POST /api/v1/platforms/pinterest` - Generate Pinterest content
- `POST /api/v1/platforms/snapchat` - Generate Snapchat content
- `POST /api/v1/platforms/website` - Generate website/blog content
- `POST /api/v1/platforms/email` - Generate email content

#### Templates
- `GET /api/v1/templates` - List all templates
- `GET /api/v1/templates/{template_id}` - Get a specific template
- `POST /api/v1/templates/{template_id}/render` - Render a template with variables
- `GET /api/v1/templates/search` - Search templates

#### Generation Management
- `GET /api/v1/generation/stats` - Get generation statistics
- `POST /api/v1/generation/cache/clear` - Clear all cached content
- `GET /api/v1/generation/cache/stats` - Get cache statistics

#### Providers
- `GET /api/v1/providers` - Get available AI providers
- `GET /api/v1/providers/current` - Get current provider information
- `POST /api/v1/providers/change` - Change the AI provider

## Project Structure

```
content_engine/
├── __init__.py
├── main.py                 # Main entry point
├── config/                 # Configuration files
│   ├── __init__.py
│   ├── settings.py         # Application settings
│   └── providers.py        # AI provider configurations
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── engine.py           # Main Content Engine
│   ├── generator.py        # Content generation logic
│   ├── providers.py        # AI provider implementations
│   └── cache.py            # Caching system
├── models/                 # Data models
│   ├── __init__.py
│   ├── content.py          # Content models
│   ├── generation.py       # Generation models
│   ├── platforms.py        # Platform-specific models
│   └── templates.py        # Template models
├── platforms/              # Platform-specific generators
│   ├── __init__.py
│   ├── base.py             # Base platform generator
│   ├── twitter.py          # Twitter/X generator
│   ├── facebook.py         # Facebook generator
│   ├── instagram.py        # Instagram generator
│   ├── linkedin.py         # LinkedIn generator
│   ├── pinterest.py        # Pinterest generator
│   ├── snapchat.py         # Snapchat generator
│   ├── website.py          # Website/Blog generator
│   └── email.py            # Email generator
├── templates/              # Templating system
│   ├── __init__.py
│   ├── manager.py          # Template manager
│   ├── renderer.py         # Template renderer
│   └── library.py          # Predefined templates
├── api/                    # API server
│   ├── __init__.py
│   ├── server.py           # FastAPI server
│   ├── routes.py           # API routes
│   └── handlers.py         # Request handlers
├── cli/                    # CLI interface
│   ├── __init__.py
│   ├── commands.py         # CLI commands
│   └── main.py             # CLI entry point
└── utils/                  # Utility functions
    └── __init__.py
```

## Examples

### Twitter Content Generation

```python
from content_engine import ContentEngine
import asyncio

async def generate_tweet():
    engine = ContentEngine()
    await engine.initialize()
    
    # Simple tweet
    tweet = await engine.generate_twitter(
        "Just launched our new AI-powered content engine! 🚀",
        use_emojis=True,
        use_hashtags=True,
        hashtag_count=3,
    )
    print(tweet.content)
    # Output: "Just launched our new AI-powered content engine! 🚀\n\n#AI #ContentCreation #Innovation"
    
    # Tweet with specific tone
    tweet = await engine.generate_twitter(
        "The future of content creation is here",
        tone="inspirational",
        use_emojis=True,
    )
    print(tweet.content)
    
    await engine.close()

asyncio.run(generate_tweet())
```

### Facebook Post Generation

```python
from content_engine import ContentEngine
import asyncio

async def generate_facebook_post():
    engine = ContentEngine()
    await engine.initialize()
    
    # Facebook post
    post = await engine.generate_facebook(
        "Announcing our new AI-powered content engine that can generate content for all social media platforms!",
        use_emojis=True,
        use_hashtags=True,
        hashtag_count=5,
    )
    print(post.content)
    
    # Album post
    from content_engine.platforms import FacebookGenerator
    fb_gen = FacebookGenerator(engine)
    album_post = await fb_gen.generate_album_post(
        images=["image1.jpg", "image2.jpg", "image3.jpg"],
        caption="Our team at the recent AI conference",
    )
    print(album_post.content)
    
    await engine.close()

asyncio.run(generate_facebook_post())
```

### Instagram Content Generation

```python
from content_engine import ContentEngine
from content_engine.platforms import InstagramGenerator
import asyncio

async def generate_instagram_content():
    engine = ContentEngine()
    await engine.initialize()
    
    # Instagram caption
    ig_gen = InstagramGenerator(engine)
    caption = await ig_gen.generate_caption(
        image_description="A beautiful sunset over the ocean with a sailboat",
    )
    print(caption.content)
    
    # Generate hashtags
    hashtags = await ig_gen.generate_hashtag_set(
        topic="travel photography",
        count=15,
    )
    print("Hashtags:", hashtags)
    
    await engine.close()

asyncio.run(generate_instagram_content())
```

### Blog Post Generation

```python
from content_engine import ContentEngine
import asyncio

async def generate_blog_post():
    engine = ContentEngine()
    await engine.initialize()
    
    # Blog post
    blog = await engine.generate_website(
        "The ultimate guide to AI-powered content creation",
        content_type="blog_post",
        tone="educational",
        style="detailed",
        min_length=1500,
        use_markdown=True,
    )
    print(blog.content)
    
    # SEO-optimized content
    seo = await engine.generate_website(
        "Best AI tools for content creation",
        content_type="seo_content",
        keyword="AI content tools",
        min_length=800,
    )
    print(seo.content)
    
    await engine.close()

asyncio.run(generate_blog_post())
```

### Batch Processing

```python
from content_engine import ContentEngine
import asyncio

async def batch_generation():
    engine = ContentEngine()
    await engine.initialize()
    
    # Generate content for multiple prompts
    prompts = [
        "Top 5 AI tools for social media",
        "How to create engaging content with AI",
        "The future of AI in marketing",
        "Best practices for AI-generated content",
    ]
    
    responses = await engine.generate_batch(
        prompts,
        platform="twitter",
        use_emojis=True,
        use_hashtags=True,
    )
    
    for i, response in enumerate(responses, 1):
        print(f"Tweet {i}: {response.content}\n")
    
    await engine.close()

asyncio.run(batch_generation())
```

### Template Usage

```python
from content_engine import ContentEngine
from content_engine.templates.manager import TemplateManager
import asyncio

async def use_templates():
    engine = ContentEngine()
    await engine.initialize()
    
    # Initialize template manager
    template_manager = TemplateManager()
    await template_manager.initialize()
    
    # Render a template
    content = await template_manager.render_template(
        template_id="twitter_basic",
        variables={
            "prompt": "Check out our new AI content engine!",
            "hashtags": "#AI #Content #Innovation",
        }
    )
    print(content)
    
    # List available templates
    templates = await template_manager.list_templates()
    for template in templates[:5]:  # Show first 5
        print(f"- {template.name} ({template.id})")
    
    await engine.close()

asyncio.run(use_templates())
```

## Configuration

### Settings

The Content Engine uses Pydantic Settings for configuration. You can configure:

- **Application Settings**: App name, version, debug mode
- **AI Providers**: API keys, models, timeouts, retry settings
- **Platform Settings**: Character limits, hashtag limits for each platform
- **Cache Settings**: Enable/disable, TTL, max size
- **Rate Limiting**: Request limits and periods

### Environment Variables

All settings can be configured via environment variables:

```bash
# Application
APP_NAME=Content Engine
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# AI Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
DEFAULT_PROVIDER=openai

# Platform Limits
TWITTER_MAX_LENGTH=280
FACEBOOK_POST_LENGTH=63206
INSTAGRAM_CAPTION_LENGTH=2200

# Cache
CACHE_ENABLED=True
CACHE_TTL=3600
MAX_CACHE_SIZE=1000
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/xghstrider/Content-engine.git
cd Content-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check content_engine/
black content_engine/

# Run type checking
mypy content_engine/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:

1. Check the [documentation](https://github.com/xghstrider/Content-engine#readme)
2. Look at existing [issues](https://github.com/xghstrider/Content-engine/issues)
3. Create a new [issue](https://github.com/xghstrider/Content-engine/issues/new)

## Roadmap

### Upcoming Features

- [ ] **Image Generation**: Support for generating images via AI models
- [ ] **Video Generation**: Support for generating video content
- [ ] **Voice Generation**: Text-to-speech and voice content generation
- [ ] **Multi-language Support**: Better support for various languages
- [ ] **Content Scheduling**: Schedule content for optimal posting times
- [ ] **Analytics Dashboard**: Track content performance and analytics
- [ ] **Team Collaboration**: Multi-user support with permissions
- [ ] **Content Calendar**: Plan and organize content in advance
- [ ] **Brand Voice**: Custom brand voice and style profiles
- [ ] **Content Repurposing**: Automatically repurpose content for different platforms

### Version History

- **v1.0.0** (Current): Initial release with comprehensive content generation support

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Pydantic](https://pydantic.dev/) for data validation
- [Click](https://click.palletsprojects.com/) for CLI interface
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [OpenAI](https://openai.com/) for AI models
- [Anthropic](https://anthropic.com/) for AI models
- [Google](https://ai.google/) for AI models

---

**Content Engine** - AI Powered Content Creation for Everyone

🌟 **Star this repository** if you find it useful!

📦 **Download** the latest version from [GitHub Releases](https://github.com/xghstrider/Content-engine/releases)

🐛 **Report bugs** and request features via [GitHub Issues](https://github.com/xghstrider/Content-engine/issues)
