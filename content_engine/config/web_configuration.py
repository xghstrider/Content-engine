"""Persistent configuration managed through the browser workspace."""

import json
import os
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from content_engine.config.providers import DEFAULT_PROVIDERS, ProviderType


class WebConfiguration:
    """Store provider profiles and reusable prompt presets outside the repo."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or Path(
            os.environ.get(
                "CONTENT_ENGINE_WEB_CONFIG",
                str(Path.home() / ".content_engine" / "web_config.json"),
            )
        )
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {"providers": {}, "prompts": {}, "default_provider": None}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as config_file:
            loaded = json.load(config_file)
        if isinstance(loaded, dict):
            self._data.update(loaded)

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as config_file:
            json.dump(self._data, config_file, indent=2)
        temporary_path.replace(self.path)

    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            providers = {name: dict(config) for name, config in DEFAULT_PROVIDERS.items()}
            providers.update({name: dict(config) for name, config in self._data["providers"].items()})
            return providers

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            configured = self._data["providers"].get(provider_id)
            if configured:
                return dict(configured)
            default = DEFAULT_PROVIDERS.get(provider_id)
            return dict(default) if default else None

    def save_provider(self, provider_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,47}", provider_id):
            raise ValueError("Provider ID must be 1-48 letters, numbers, underscores, or hyphens")
        provider_type = config.get("provider_type", "openai")
        if provider_type not in {item.value for item in ProviderType}:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        if not config.get("model"):
            raise ValueError("A model name is required")

        with self._lock:
            previous = self._data["providers"].get(provider_id, {})
            saved = {
                "provider_type": provider_type,
                "base_url": str(config.get("base_url", "")).rstrip("/"),
                "model": str(config["model"]),
                "api_key": config.get("api_key") or previous.get("api_key"),
                "timeout": int(config.get("timeout", 30)),
                "max_tokens": int(config.get("max_tokens", 4096)),
                "temperature": float(config.get("temperature", 0.7)),
            }
            if provider_type == ProviderType.LOCAL.value and config.get("model_path"):
                saved["model_path"] = str(config["model_path"])
            self._data["providers"][provider_id] = saved
            self._save()
            return dict(saved)

    def delete_provider(self, provider_id: str) -> bool:
        if provider_id in DEFAULT_PROVIDERS:
            raise ValueError("Built-in provider profiles cannot be deleted")
        with self._lock:
            removed = self._data["providers"].pop(provider_id, None) is not None
            if removed:
                if self._data.get("default_provider") == provider_id:
                    self._data["default_provider"] = None
                self._save()
            return removed

    def get_default_provider(self) -> Optional[str]:
        with self._lock:
            return self._data.get("default_provider")

    def effective_default_provider(self) -> Optional[str]:
        with self._lock:
            return self._data.get("default_provider") or "openai"

    def set_default_provider(self, provider_id: str) -> None:
        if provider_id not in self.list_providers():
            raise ValueError(f"Unknown provider: {provider_id}")
        with self._lock:
            self._data["default_provider"] = provider_id
            self._save()

    def list_prompts(self) -> List[Dict[str, str]]:
        with self._lock:
            return [dict(prompt, id=prompt_id) for prompt_id, prompt in self._data["prompts"].items()]

    def save_prompt(self, prompt_id: str, prompt: Dict[str, Any]) -> Dict[str, str]:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,47}", prompt_id):
            raise ValueError("Prompt ID must be 1-48 letters, numbers, underscores, or hyphens")
        name = str(prompt.get("name", "")).strip()
        instructions = str(prompt.get("instructions", "")).strip()
        if not name or not instructions:
            raise ValueError("Prompt name and instructions are required")
        saved = {"name": name, "instructions": instructions}
        with self._lock:
            self._data["prompts"][prompt_id] = saved
            self._save()
        return dict(saved, id=prompt_id)

    def delete_prompt(self, prompt_id: str) -> bool:
        with self._lock:
            removed = self._data["prompts"].pop(prompt_id, None) is not None
            if removed:
                self._save()
            return removed


web_configuration = WebConfiguration()