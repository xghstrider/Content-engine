"""
Template library with predefined templates
"""

from typing import Dict, List

from content_engine.models.templates import (
    Template,
    TemplateCategory,
    TemplateType,
    TemplateVariable,
)


class TemplateLibrary:
    """Library of predefined templates for various platforms"""
    
    @staticmethod
    def get_social_media_templates() -> List[Template]:
        """Get social media templates"""
        return [
            # Twitter templates
            Template(
                id="twitter_basic",
                name="Twitter Basic",
                description="Basic Twitter/X post template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{prompt}\n\n{hashtags}",
                variables=[
                    TemplateVariable(
                        name="prompt",
                        description="Main content or message",
                        required=True,
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags",
                        default_value="",
                    ),
                ],
                platform="twitter",
            ),
            
            Template(
                id="twitter_thread",
                name="Twitter Thread",
                description="Twitter thread post template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{thread_position}/{total_tweets}\n\n{content}\n\n{hashtags}",
                variables=[
                    TemplateVariable(
                        name="thread_position",
                        description="Position in thread (e.g., 1, 2, 3)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="total_tweets",
                        description="Total number of tweets in thread",
                        required=True,
                    ),
                    TemplateVariable(
                        name="content",
                        description="Main content for this tweet",
                        required=True,
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags",
                        default_value="",
                    ),
                ],
                platform="twitter",
            ),
            
            # Facebook templates
            Template(
                id="facebook_post",
                name="Facebook Post",
                description="Basic Facebook post template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{content}\n\n{hashtags}",
                variables=[
                    TemplateVariable(
                        name="content",
                        description="Main post content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags",
                        default_value="",
                    ),
                ],
                platform="facebook",
            ),
            
            Template(
                id="facebook_link",
                name="Facebook Link Post",
                description="Facebook link post template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{introduction}\n\n{link_url}\n\n{description}\n\n{hashtags}",
                variables=[
                    TemplateVariable(
                        name="introduction",
                        description="Introduction text",
                        required=True,
                    ),
                    TemplateVariable(
                        name="link_url",
                        description="URL to share",
                        required=True,
                    ),
                    TemplateVariable(
                        name="description",
                        description="Description of the link",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags",
                        default_value="",
                    ),
                ],
                platform="facebook",
            ),
            
            # Instagram templates
            Template(
                id="instagram_caption",
                name="Instagram Caption",
                description="Instagram post caption template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{emoji} {caption}\n\n{hashtags}",
                variables=[
                    TemplateVariable(
                        name="emoji",
                        description="Emoji to start with",
                        default_value="📸",
                    ),
                    TemplateVariable(
                        name="caption",
                        description="Main caption text",
                        required=True,
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags (one per line)",
                        default_value="",
                    ),
                ],
                platform="instagram",
            ),
            
            Template(
                id="instagram_story",
                name="Instagram Story",
                description="Instagram story template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{text} {emoji}",
                variables=[
                    TemplateVariable(
                        name="text",
                        description="Story text",
                        required=True,
                    ),
                    TemplateVariable(
                        name="emoji",
                        description="Emoji to add",
                        default_value="✨",
                    ),
                ],
                platform="instagram",
            ),
            
            # LinkedIn templates
            Template(
                id="linkedin_post",
                name="LinkedIn Post",
                description="LinkedIn post template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="{content}\n\n{hashtags}",
                variables=[
                    TemplateVariable(
                        name="content",
                        description="Main post content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags",
                        default_value="",
                    ),
                ],
                platform="linkedin",
            ),
            
            Template(
                id="linkedin_article",
                name="LinkedIn Article",
                description="LinkedIn article template",
                template_type=TemplateType.MARKDOWN,
                category=TemplateCategory.SOCIAL_MEDIA,
                content="""# {title}

{introduction}

## {section1_title}
{section1_content}

## {section2_title}
{section2_content}

## {section3_title}
{section3_content}

{conclusion}

{hashtags}""",
                variables=[
                    TemplateVariable(
                        name="title",
                        description="Article title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="introduction",
                        description="Introduction paragraph",
                        required=True,
                    ),
                    TemplateVariable(
                        name="section1_title",
                        description="First section title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="section1_content",
                        description="First section content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="section2_title",
                        description="Second section title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="section2_content",
                        description="Second section content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="section3_title",
                        description="Third section title",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="section3_content",
                        description="Third section content",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="conclusion",
                        description="Conclusion paragraph",
                        required=True,
                    ),
                    TemplateVariable(
                        name="hashtags",
                        description="Relevant hashtags",
                        default_value="",
                    ),
                ],
                platform="linkedin",
            ),
        ]
    
    @staticmethod
    def get_blog_templates() -> List[Template]:
        """Get blog templates"""
        return [
            Template(
                id="blog_post",
                name="Blog Post",
                description="Standard blog post template",
                template_type=TemplateType.MARKDOWN,
                category=TemplateCategory.BLOG,
                content="""# {title}

{excerpt}

---

{content}

---

{author_bio}""",
                variables=[
                    TemplateVariable(
                        name="title",
                        description="Blog post title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="excerpt",
                        description="Short excerpt/summary",
                        required=True,
                    ),
                    TemplateVariable(
                        name="content",
                        description="Main blog content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="author_bio",
                        description="Author biography",
                        default_value="",
                    ),
                ],
            ),
            
            Template(
                id="blog_listicle",
                name="Listicle Blog Post",
                description="List-style blog post template",
                template_type=TemplateType.MARKDOWN,
                category=TemplateCategory.BLOG,
                content="""# {title}

{introduction}

{items}

{conclusion}""",
                variables=[
                    TemplateVariable(
                        name="title",
                        description="Blog post title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="introduction",
                        description="Introduction paragraph",
                        required=True,
                    ),
                    TemplateVariable(
                        name="items",
                        description="List items (one per line with number)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="conclusion",
                        description="Conclusion paragraph",
                        required=True,
                    ),
                ],
            ),
            
            Template(
                id="blog_tutorial",
                name="Tutorial Blog Post",
                description="Step-by-step tutorial template",
                template_type=TemplateType.MARKDOWN,
                category=TemplateCategory.BLOG,
                content="""# {title}

{introduction}

## Prerequisites
{prerequisites}

## Step 1: {step1_title}
{step1_content}

## Step 2: {step2_title}
{step2_content}

## Step 3: {step3_title}
{step3_content}

## Step 4: {step4_title}
{step4_content}

{conclusion}""",
                variables=[
                    TemplateVariable(
                        name="title",
                        description="Tutorial title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="introduction",
                        description="Introduction",
                        required=True,
                    ),
                    TemplateVariable(
                        name="prerequisites",
                        description="Prerequisites for the tutorial",
                        default_value="None",
                    ),
                    TemplateVariable(
                        name="step1_title",
                        description="Step 1 title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="step1_content",
                        description="Step 1 content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="step2_title",
                        description="Step 2 title",
                        required=True,
                    ),
                    TemplateVariable(
                        name="step2_content",
                        description="Step 2 content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="step3_title",
                        description="Step 3 title",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="step3_content",
                        description="Step 3 content",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="step4_title",
                        description="Step 4 title",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="step4_content",
                        description="Step 4 content",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="conclusion",
                        description="Conclusion",
                        required=True,
                    ),
                ],
            ),
        ]
    
    @staticmethod
    def get_email_templates() -> List[Template]:
        """Get email templates"""
        return [
            Template(
                id="email_basic",
                name="Basic Email",
                description="Basic email template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.EMAIL,
                content="""Subject: {subject}

{greeting}

{body}

{closing}
{signature}""",
                variables=[
                    TemplateVariable(
                        name="subject",
                        description="Email subject",
                        required=True,
                    ),
                    TemplateVariable(
                        name="greeting",
                        description="Greeting (e.g., Dear John, Hi there)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="body",
                        description="Email body content",
                        required=True,
                    ),
                    TemplateVariable(
                        name="closing",
                        description="Closing (e.g., Best regards, Sincerely)",
                        default_value="Best regards",
                    ),
                    TemplateVariable(
                        name="signature",
                        description="Your name/signature",
                        default_value="",
                    ),
                ],
            ),
            
            Template(
                id="email_newsletter",
                name="Newsletter Email",
                description="Newsletter email template",
                template_type=TemplateType.HTML,
                category=TemplateCategory.EMAIL,
                content="""<html>
<head>
    <title>{subject}</title>
</head>
<body>
    <h1>{header}</h1>
    
    <p>{introduction}</p>
    
    {articles}
    
    <p>{closing}</p>
    
    <footer>
        <p>{unsubscribe_link}</p>
    </footer>
</body>
</html>""",
                variables=[
                    TemplateVariable(
                        name="subject",
                        description="Newsletter subject",
                        required=True,
                    ),
                    TemplateVariable(
                        name="header",
                        description="Newsletter header",
                        required=True,
                    ),
                    TemplateVariable(
                        name="introduction",
                        description="Introduction text",
                        required=True,
                    ),
                    TemplateVariable(
                        name="articles",
                        description="Article content (HTML)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="closing",
                        description="Closing text",
                        required=True,
                    ),
                    TemplateVariable(
                        name="unsubscribe_link",
                        description="Unsubscribe link",
                        required=True,
                    ),
                ],
            ),
            
            Template(
                id="email_promotional",
                name="Promotional Email",
                description="Promotional email template",
                template_type=TemplateType.TEXT,
                category=TemplateCategory.EMAIL,
                content="""Subject: {subject}

{greeting}

{offer_introduction}

{offer_details}

{call_to_action}

{closing}
{signature}""",
                variables=[
                    TemplateVariable(
                        name="subject",
                        description="Email subject",
                        required=True,
                    ),
                    TemplateVariable(
                        name="greeting",
                        description="Greeting",
                        required=True,
                    ),
                    TemplateVariable(
                        name="offer_introduction",
                        description="Introduction to the offer",
                        required=True,
                    ),
                    TemplateVariable(
                        name="offer_details",
                        description="Details of the offer",
                        required=True,
                    ),
                    TemplateVariable(
                        name="call_to_action",
                        description="Call to action (e.g., Click here, Buy now)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="closing",
                        description="Closing",
                        default_value="Best regards",
                    ),
                    TemplateVariable(
                        name="signature",
                        description="Signature",
                        default_value="",
                    ),
                ],
            ),
        ]
    
    @staticmethod
    def get_seo_templates() -> List[Template]:
        """Get SEO templates"""
        return [
            Template(
                id="seo_blog",
                name="SEO Blog Post",
                description="SEO-optimized blog post template",
                template_type=TemplateType.MARKDOWN,
                category=TemplateCategory.SEO,
                content="""# {title}

{meta_description}

---

{introduction}

## {h2_1}
{h2_1_content}

## {h2_2}
{h2_2_content}

## {h2_3}
{h2_3_content}

{conclusion}

---

{keywords}""",
                variables=[
                    TemplateVariable(
                        name="title",
                        description="Title with primary keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="meta_description",
                        description="Meta description (150-160 chars)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="introduction",
                        description="Introduction with primary keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="h2_1",
                        description="First H2 heading with keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="h2_1_content",
                        description="Content for first section",
                        required=True,
                    ),
                    TemplateVariable(
                        name="h2_2",
                        description="Second H2 heading with keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="h2_2_content",
                        description="Content for second section",
                        required=True,
                    ),
                    TemplateVariable(
                        name="h2_3",
                        description="Third H2 heading with keyword",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="h2_3_content",
                        description="Content for third section",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="conclusion",
                        description="Conclusion with call-to-action",
                        required=True,
                    ),
                    TemplateVariable(
                        name="keywords",
                        description="SEO keywords (comma separated)",
                        default_value="",
                    ),
                ],
            ),
            
            Template(
                id="seo_product",
                name="SEO Product Page",
                description="SEO-optimized product page template",
                template_type=TemplateType.HTML,
                category=TemplateCategory.SEO,
                content="""<html>
<head>
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
</head>
<body>
    <h1>{product_name}</h1>
    
    <p>{short_description}</p>
    
    <h2>Features</h2>
    <ul>
    {features}
    </ul>
    
    <h2>Benefits</h2>
    <ul>
    {benefits}
    </ul>
    
    <h2>Specifications</h2>
    {specifications}
    
    {call_to_action}
</body>
</html>""",
                variables=[
                    TemplateVariable(
                        name="title",
                        description="Page title with keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="meta_description",
                        description="Meta description (150-160 chars)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="product_name",
                        description="Product name with keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="short_description",
                        description="Short description with keyword",
                        required=True,
                    ),
                    TemplateVariable(
                        name="features",
                        description="Features list (HTML <li> items)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="benefits",
                        description="Benefits list (HTML <li> items)",
                        required=True,
                    ),
                    TemplateVariable(
                        name="specifications",
                        description="Specifications table or list",
                        default_value="",
                    ),
                    TemplateVariable(
                        name="call_to_action",
                        description="Call to action (e.g., Add to cart button)",
                        required=True,
                    ),
                ],
            ),
        ]
    
    @staticmethod
    def get_all_templates() -> List[Template]:
        """Get all predefined templates"""
        templates = []
        templates.extend(TemplateLibrary.get_social_media_templates())
        templates.extend(TemplateLibrary.get_blog_templates())
        templates.extend(TemplateLibrary.get_email_templates())
        templates.extend(TemplateLibrary.get_seo_templates())
        return templates
    
    @staticmethod
    def get_templates_by_category() -> Dict[str, List[Template]]:
        """Get templates grouped by category"""
        categories = {}
        
        for template in TemplateLibrary.get_all_templates():
            category_name = template.category.value.replace('_', ' ').title()
            if category_name not in categories:
                categories[category_name] = []
            categories[category_name].append(template)
        
        return categories
