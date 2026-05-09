import json
from pathlib import Path
from pydantic import BaseModel


class ProviderConfig(BaseModel):
    name: str  # "openai", "anthropic", "dashscope"
    api_key: str
    base_url: str | None = None
    default_model: str
    extra_body: dict | None = None


class SkillConfig(BaseModel):
    provider: str  # references a provider name
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096


class AIConfig(BaseModel):
    providers: dict[str, ProviderConfig]
    skills: dict[str, SkillConfig] = {}
    features: dict[str, SkillConfig] = {}


_config: AIConfig | None = None
CONFIG_PATH = Path(__file__).parent.parent / "ai_config.json"


def load_config() -> AIConfig:
    global _config
    if _config is not None:
        return _config
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"AI config not found. Please create {CONFIG_PATH} with your API keys. "
            "See ai_config.example.json for reference."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    _config = AIConfig(**data)
    return _config


def reload_config() -> AIConfig:
    global _config
    _config = None
    return load_config()
