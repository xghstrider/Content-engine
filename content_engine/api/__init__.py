"""API package exports for Content Engine."""

__all__ = [
    "app",
    "router",
    "ContentHandler",
    "PlatformHandler",
    "TemplateHandler",
    "GenerationHandler",
]


def __getattr__(name):
    """Lazily resolve API symbols to avoid circular imports during startup."""
    if name == "app":
        from content_engine.api.server import app
        return app
    if name == "router":
        from content_engine.api.routes import router
        return router
    if name in {"ContentHandler", "PlatformHandler", "TemplateHandler", "GenerationHandler"}:
        from content_engine.api.handlers import (
            ContentHandler,
            PlatformHandler,
            TemplateHandler,
            GenerationHandler,
        )
        return {
            "ContentHandler": ContentHandler,
            "PlatformHandler": PlatformHandler,
            "TemplateHandler": TemplateHandler,
            "GenerationHandler": GenerationHandler,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
