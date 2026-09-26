from content_engine.config.web_configuration import WebConfiguration
from content_engine.core.providers import ProviderFactory


def test_web_configuration_save_provider_and_prompt(tmp_path):
    config = WebConfiguration(path=tmp_path / "web_config.json")

    saved_provider = config.save_provider(
        "brand_openai",
        {
            "provider_type": "openai",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "api_key": "secret-key",
            "timeout": 45,
            "max_tokens": 2048,
            "temperature": 0.8,
        },
    )
    assert saved_provider["model"] == "gpt-4o-mini"
    assert "brand_openai" in config.list_providers()

    saved_prompt = config.save_prompt(
        "launch",
        {"name": "Launch", "instructions": "Write a concise launch announcement."},
    )
    assert saved_prompt["id"] == "launch"
    assert config.list_prompts()[0]["id"] == "launch"


def test_provider_factory_accepts_custom_web_provider(monkeypatch):
    from content_engine.config.web_configuration import web_configuration

    web_configuration._data["providers"]["acme_openai"] = {
        "provider_type": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "api_key": "secret-key",
        "timeout": 45,
        "max_tokens": 2048,
        "temperature": 0.8,
    }
    monkeypatch.setattr(
        "content_engine.config.settings.get_settings",
        lambda: type(
            "SettingsStub",
            (),
            {
                "ai": type(
                    "AIStub",
                    (),
                    {
                        "openai_api_key": "secret-key",
                        "openai_base_url": "https://api.openai.com/v1",
                        "openai_model": "gpt-4o-mini",
                        "anthropic_api_key": None,
                        "anthropic_base_url": "https://api.anthropic.com",
                        "anthropic_model": "claude-3-sonnet-20240229",
                        "google_api_key": None,
                        "google_model": "gemini-1.5-pro",
                        "local_model_path": None,
                        "default_provider": "acme_openai",
                    },
                )(),
            },
        )(),
    )

    provider = ProviderFactory.create_provider("acme_openai")
    assert provider.config.provider_type.value == "openai"
    assert provider.config.model == "gpt-4o-mini"

    web_configuration._data["providers"].pop("acme_openai", None)
