"""
AI Provider configurations
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ProviderType(Enum):
    """Supported AI Provider Types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    HUGGINGFACE = "huggingface"


@dataclass
class AIProviderConfig:
    """Configuration for an AI Provider"""
    
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: str = ""
    model: str = ""
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Additional provider-specific settings
    extra_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider_type": self.provider_type.value,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            **self.extra_config
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "AIProviderConfig":
        """Create from dictionary"""
        provider_type = ProviderType(config.get("provider_type", "openai"))
        return cls(
            provider_type=provider_type,
            api_key=config.get("api_key"),
            base_url=config.get("base_url", ""),
            model=config.get("model", ""),
            timeout=config.get("timeout", 30),
            max_retries=config.get("max_retries", 3),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 4096),
            top_p=config.get("top_p", 0.9),
            frequency_penalty=config.get("frequency_penalty", 0.0),
            presence_penalty=config.get("presence_penalty", 0.0),
            extra_config={k: v for k, v in config.items() 
                         if k not in ["provider_type", "api_key", "base_url", "model", 
                                      "timeout", "max_retries", "temperature", "max_tokens",
                                      "top_p", "frequency_penalty", "presence_penalty"]}
        )


# Default provider configurations
DEFAULT_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "provider_type": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4-turbo-preview",
        "temperature": 0.7,
        "max_tokens": 4096,
    },
    "anthropic": {
        "provider_type": "anthropic",
        "base_url": "https://api.anthropic.com",
        "model": "claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 4096,
    },
    "google": {
        "provider_type": "google",
        "base_url": "https://generativelanguage.googleapis.com",
        "model": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_tokens": 4096,
    },
    "local": {
        "provider_type": "local",
        "model": "llama-2-7b-chat",
        "temperature": 0.7,
        "max_tokens": 2048,
    },
}
