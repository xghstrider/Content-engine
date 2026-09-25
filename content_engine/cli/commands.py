"""
CLI commands for Content Engine
"""

import asyncio
import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from content_engine.config.settings import get_settings, Settings
from content_engine.core.cache import ContentCache
from content_engine.core.engine import ContentEngine
from content_engine.models.content import (
    ContentRequest,
    ContentResponse,
    ContentType,
    ContentTone,
    ContentStyle,
    PlatformType,
)
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

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)

# Rich console
console = Console()

# Global engine instance
_engine: Optional[ContentEngine] = None


@click.group()
@click.version_option(version="1.0.0", message="Content Engine CLI v1.0.0")
def cli():
    """Content Engine CLI - AI Powered Content Creation"""
    pass


@cli.command()
@click.option("--provider", "-p", default=None, help="AI provider to use")
@click.option("--model", "-m", default=None, help="Model to use")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def init(provider: Optional[str], model: Optional[str], debug: bool):
    """Initialize the Content Engine"""
    global _engine
    
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Initializing Content Engine...", total=None)
        
        try:
            _engine = ContentEngine()
            asyncio.run(_engine.initialize())
            
            progress.remove_task(task)
            console.print("[green]✓[/green] Content Engine initialized successfully")
            
            # Show configuration
            settings = get_settings()
            table = Table(title="Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("App Name", settings.app_name)
            table.add_row("App Version", settings.app_version)
            table.add_row("Default Provider", settings.ai.default_provider)
            table.add_row("Cache Enabled", str(settings.cache.cache_enabled))
            
            console.print(table)
            
        except Exception as e:
            progress.remove_task(task)
            console.print(f"[red]✗[/red] Failed to initialize: {e}")
            sys.exit(1)


@cli.command()
@click.argument("prompt", type=str)
@click.option("--platform", "-P", type=str, default=None, help="Target platform")
@click.option("--type", "-t", type=str, default="text", help="Content type")
@click.option("--tone", type=str, default=None, help="Tone of content")
@click.option("--style", type=str, default=None, help="Writing style")
@click.option("--length", "-l", type=int, default=None, help="Maximum length")
@click.option("--emojis", is_flag=True, help="Include emojis")
@click.option("--hashtags", is_flag=True, help="Include hashtags")
@click.option("--output", "-o", type=str, default=None, help="Output file")
def generate(
    prompt: str,
    platform: Optional[str],
    type: str,
    tone: Optional[str],
    style: Optional[str],
    length: Optional[int],
    emojis: bool,
    hashtags: bool,
    output: Optional[str],
):
    """Generate content"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        # Build request
        request_data = {
            "prompt": prompt,
            "content_type": type,
        }
        
        if platform:
            request_data["platform"] = platform
        if tone:
            request_data["tone"] = tone
        if style:
            request_data["style"] = style
        if length:
            request_data["max_length"] = length
        if emojis:
            request_data["use_emojis"] = True
        if hashtags:
            request_data["use_hashtags"] = True
        
        request = ContentRequest(**request_data)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating content...", total=None)
            
            response = asyncio.run(_engine.generate_advanced(request))
            
            progress.remove_task(task)
        
        # Display result
        console.print()
        console.print(Panel.fit("[bold]Generated Content[/bold]", border_style="blue"))
        console.print()
        console.print(response.content)
        console.print()
        
        # Show metadata
        table = Table(title="Metadata")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Platform", response.platform.value if response.platform else "N/A")
        table.add_row("Content Type", response.content_type.value)
        table.add_row("Provider", response.provider)
        table.add_row("Model", response.model)
        table.add_row("Character Count", str(response.character_count))
        table.add_row("Word Count", str(response.word_count))
        table.add_row("Generation Time", f"{response.generation_time:.2f}s")
        
        console.print(table)
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(response.content)
            console.print(f"[green]✓[/green] Content saved to {output}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Generation failed: {e}")
        logger.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument("prompt", type=str)
@click.option("--count", "-c", type=int, default=3, help="Number of alternatives")
@click.option("--platform", "-P", type=str, default=None, help="Target platform")
def alternatives(prompt: str, count: int, platform: Optional[str]):
    """Generate multiple alternatives"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating alternatives...", total=None)
            
            request = ContentRequest(
                prompt=prompt,
                platform=platform,
            )
            
            alternatives = asyncio.run(_engine.create_alternatives(request, count))
            
            progress.remove_task(task)
        
        console.print()
        console.print(Panel.fit(f"[bold]{count} Alternatives for: {prompt}[/bold]", border_style="blue"))
        console.print()
        
        for i, alt in enumerate(alternatives, 1):
            console.print(f"[bold cyan]Alternative {i}:[/bold cyan]")
            console.print(alt.content)
            console.print()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate alternatives: {e}")
        sys.exit(1)


@cli.group()
def platform():
    """Platform-specific commands"""
    pass


@platform.command(name="twitter")
@click.argument("prompt", type=str)
@click.option("--thread", is_flag=True, help="Generate a thread")
@click.option("--tweet-count", type=int, default=3, help="Number of tweets in thread")
def twitter(prompt: str, thread: bool, tweet_count: int):
    """Generate Twitter/X content"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        if thread:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating Twitter thread...", total=None)
                
                generator = TwitterGenerator(_engine)
                responses = asyncio.run(generator.generate_thread(prompt, tweet_count))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit(f"[bold]Twitter Thread: {prompt}[/bold]", border_style="blue"))
            console.print()
            
            for i, resp in enumerate(responses, 1):
                console.print(f"[bold cyan]Tweet {i}/{tweet_count}:[/bold cyan]")
                console.print(resp.content)
                console.print()
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating Twitter content...", total=None)
                
                response = asyncio.run(_engine.generate_twitter(prompt))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit("[bold]Twitter Content[/bold]", border_style="blue"))
            console.print()
            console.print(response.content)
            console.print()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")
        sys.exit(1)


@platform.command(name="facebook")
@click.argument("prompt", type=str)
def facebook(prompt: str):
    """Generate Facebook content"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating Facebook content...", total=None)
            
            response = asyncio.run(_engine.generate_facebook(prompt))
            
            progress.remove_task(task)
        
        console.print()
        console.print(Panel.fit("[bold]Facebook Content[/bold]", border_style="blue"))
        console.print()
        console.print(response.content)
        console.print()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")
        sys.exit(1)


@platform.command(name="instagram")
@click.argument("prompt", type=str)
@click.option("--caption", is_flag=True, help="Generate a caption")
@click.option("--story", is_flag=True, help="Generate story content")
def instagram(prompt: str, caption: bool, story: bool):
    """Generate Instagram content"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        if caption:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating Instagram caption...", total=None)
                
                generator = InstagramGenerator(_engine)
                response = asyncio.run(generator.generate_caption(prompt))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit("[bold]Instagram Caption[/bold]", border_style="blue"))
            console.print()
            console.print(response.content)
            console.print()
        elif story:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating Instagram story...", total=None)
                
                generator = InstagramGenerator(_engine)
                response = asyncio.run(generator.generate_story_content(prompt))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit("[bold]Instagram Story[/bold]", border_style="blue"))
            console.print()
            console.print(response.content)
            console.print()
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating Instagram content...", total=None)
                
                response = asyncio.run(_engine.generate_instagram(prompt))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit("[bold]Instagram Content[/bold]", border_style="blue"))
            console.print()
            console.print(response.content)
            console.print()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")
        sys.exit(1)


@platform.command(name="linkedin")
@click.argument("prompt", type=str)
@click.option("--article", is_flag=True, help="Generate an article")
def linkedin(prompt: str, article: bool):
    """Generate LinkedIn content"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        if article:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating LinkedIn article...", total=None)
                
                generator = LinkedInGenerator(_engine)
                response = asyncio.run(generator.generate_article(
                    title=prompt,
                    outline=["Introduction", "Main Content", "Conclusion"]
                ))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit("[bold]LinkedIn Article[/bold]", border_style="blue"))
            console.print()
            console.print(response.content)
            console.print()
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating LinkedIn content...", total=None)
                
                response = asyncio.run(_engine.generate_linkedin(prompt))
                
                progress.remove_task(task)
            
            console.print()
            console.print(Panel.fit("[bold]LinkedIn Content[/bold]", border_style="blue"))
            console.print()
            console.print(response.content)
            console.print()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--all", is_flag=True, help="Show all platforms")
def platforms(all: bool):
    """List available platforms"""
    platforms = [
        ("Twitter/X", "twitter", "Short, engaging posts with hashtags"),
        ("Facebook", "facebook", "Longer posts with media support"),
        ("Instagram", "instagram", "Visual content with captions and hashtags"),
        ("LinkedIn", "linkedin", "Professional content and articles"),
        ("Pinterest", "pinterest", "Visual discovery with descriptions"),
        ("Snapchat", "snapchat", "Ephemeral, casual content"),
        ("Website/Blog", "web", "Long-form content, articles, pages"),
        ("Email", "email", "Email content, newsletters, promotional"),
    ]
    
    table = Table(title="Available Platforms")
    table.add_column("Platform", style="cyan")
    table.add_column("ID", style="magenta")
    table.add_column("Description", style="white")
    
    for name, platform_id, description in platforms:
        table.add_row(name, platform_id, description)
    
    console.print(table)
    
    if all:
        console.print()
        console.print("[bold]Content Types:[/bold]")
        for ct in ContentType:
            console.print(f"  - {ct.value}")
        
        console.print()
        console.print("[bold]Tones:[/bold]")
        for tone in ContentTone:
            console.print(f"  - {tone.value}")
        
        console.print()
        console.print("[bold]Styles:[/bold]")
        for style in ContentStyle:
            console.print(f"  - {style.value}")


@cli.command()
@click.option("--stats", is_flag=True, help="Show cache statistics")
@click.option("--clear", is_flag=True, help="Clear the cache")
def cache(stats: bool, clear: bool):
    """Manage the content cache"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        if clear:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Clearing cache...", total=None)
                
                count = asyncio.run(_engine.clear_cache())
                
                progress.remove_task(task)
            
            console.print(f"[green]✓[/green] Cleared {count} cached items")
        
        if stats or (not clear and not stats):
            cache_stats = asyncio.run(_engine.get_cache_stats())
            
            table = Table(title="Cache Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in cache_stats.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Cache operation failed: {e}")
        sys.exit(1)


@cli.command()
def info():
    """Show system information"""
    global _engine
    
    settings = get_settings()
    
    console.print(Panel.fit("[bold]Content Engine[/bold]", border_style="blue"))
    console.print()
    
    table = Table(title="System Information")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    
    table.add_row("App Name", settings.app_name)
    table.add_row("Version", settings.app_version)
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Cache Enabled", str(settings.cache.cache_enabled))
    
    if _engine:
        table.add_row("Engine", "Running")
    else:
        table.add_row("Engine", "Not initialized")
    
    console.print(table)
    
    console.print()
    console.print("[bold]AI Providers:[/bold]")
    console.print(f"  Default: {settings.ai.default_provider}")
    console.print(f"  OpenAI: {'Configured' if settings.ai.openai_api_key else 'Not configured'}")
    console.print(f"  Anthropic: {'Configured' if settings.ai.anthropic_api_key else 'Not configured'}")
    console.print(f"  Google: {'Configured' if settings.ai.google_api_key else 'Not configured'}")
    console.print(f"  Local: {'Configured' if settings.ai.local_model_path else 'Not configured'}")


@cli.command()
@click.argument("provider", type=str)
def provider(provider: str):
    """Change the AI provider"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        asyncio.run(_engine.change_provider(provider))
        console.print(f"[green]✓[/green] Provider changed to {provider}")
        
        # Show current provider info
        info = asyncio.run(_engine.get_provider_info())
        table = Table(title="Current Provider")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        for key, value in info.items():
            table.add_row(str(key), str(value))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to change provider: {e}")
        sys.exit(1)


@cli.command()
@click.argument("content", type=str)
def analyze(content: str):
    """Analyze existing content"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing content...", total=None)
            
            analysis = asyncio.run(_engine.analyze_content(content))
            
            progress.remove_task(task)
        
        console.print()
        console.print(Panel.fit("[bold]Content Analysis[/bold]", border_style="blue"))
        console.print()
        
        table = Table()
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        for key, value in analysis.items():
            if isinstance(value, list):
                value = ", ".join(value) if len(value) <= 3 else f"{len(value)} items"
            table.add_row(str(key), str(value))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Analysis failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def shell(interactive: bool):
    """Start an interactive shell"""
    global _engine
    
    if _engine is None:
        console.print("[yellow]Initializing Content Engine...[/yellow]")
        _engine = ContentEngine()
        asyncio.run(_engine.initialize())
    
    console.print(Panel.fit("[bold]Content Engine Interactive Shell[/bold]", border_style="blue"))
    console.print()
    console.print("Type 'help' for available commands, 'quit' to exit")
    console.print()
    
    while True:
        try:
            command = input(">>> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if command.lower() == 'help':
                console.print("""
Available commands:
  generate <prompt> [--platform <platform>] [--type <type>] - Generate content
  platforms - List available platforms
  provider <name> - Change AI provider
  info - Show system information
  cache [--stats] [--clear] - Manage cache
  quit/exit/q - Exit the shell
                """)
                continue
            
            if command.lower().startswith('generate '):
                parts = command.split()
                prompt = ' '.join(parts[1:])
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Generating...", total=None)
                    
                    response = asyncio.run(_engine.generate(prompt))
                    
                    progress.remove_task(task)
                
                console.print()
                console.print(response.content)
                console.print()
                continue
            
            if command.lower() == 'platforms':
                platforms = [
                    ("Twitter/X", "twitter"),
                    ("Facebook", "facebook"),
                    ("Instagram", "instagram"),
                    ("LinkedIn", "linkedin"),
                    ("Pinterest", "pinterest"),
                    ("Snapchat", "snapchat"),
                    ("Website/Blog", "web"),
                    ("Email", "email"),
                ]
                
                table = Table(title="Available Platforms")
                table.add_column("Platform", style="cyan")
                table.add_column("ID", style="magenta")
                
                for name, platform_id in platforms:
                    table.add_row(name, platform_id)
                
                console.print(table)
                continue
            
            if command.lower().startswith('provider '):
                provider = command.split()[1]
                asyncio.run(_engine.change_provider(provider))
                console.print(f"[green]✓[/green] Provider changed to {provider}")
                continue
            
            if command.lower() == 'info':
                settings = get_settings()
                table = Table(title="System Information")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="magenta")
                table.add_row("App Name", settings.app_name)
                table.add_row("Version", settings.app_version)
                table.add_row("Engine", "Running")
                console.print(table)
                continue
            
            if command.lower().startswith('cache '):
                parts = command.split()
                if len(parts) > 1 and parts[1] == '--stats':
                    cache_stats = asyncio.run(_engine.get_cache_stats())
                    table = Table(title="Cache Statistics")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value", style="magenta")
                    for key, value in cache_stats.items():
                        table.add_row(str(key), str(value))
                    console.print(table)
                elif len(parts) > 1 and parts[1] == '--clear':
                    count = asyncio.run(_engine.clear_cache())
                    console.print(f"[green]✓[/green] Cleared {count} cached items")
                else:
                    console.print("Usage: cache [--stats] [--clear]")
                continue
            
            console.print(f"Unknown command: {command}")
            
        except KeyboardInterrupt:
            console.print()
            console.print("[yellow]Use 'quit' to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")


if __name__ == "__main__":
    cli()
