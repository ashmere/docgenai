# In this file, we will handle loading configuration from config.yaml
# and environment variables.

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    name: str
    hugging_face_token: Optional[str] = None
    quantization: str = "8bit"  # Options: "none", "8bit", "4bit"
    session_cache: bool = True  # Keep model in memory for session


@dataclass
class CacheConfig:
    enabled: bool = True
    generation_cache: bool = True  # Cache generation results
    cache_dir: Path = Path(".cache/docgenai")
    max_cache_size_mb: int = 1000  # Maximum cache size in MB


@dataclass
class OutputConfig:
    dir: Path
    filename_template: str


@dataclass
class TemplatesConfig:
    dir: Path
    doc_template: str
    style_guide: str


@dataclass
class AppConfig:
    model: ModelConfig
    output: OutputConfig
    templates: TemplatesConfig
    cache: CacheConfig


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Loads configuration from a YAML file.

    The Hugging Face token is read from the HUGGING_FACE_TOKEN environment
    variable first, with the config file value as a fallback.
    """
    if config_path is None:
        config_path = Path("config.yaml")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    # Get Hugging Face token from environment variable first, then config
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    if not hf_token:
        hf_token = config_data.get("model", {}).get("hugging_face_token")
        # Don't use placeholder tokens
        if hf_token == "YOUR_HUGGING_FACE_TOKEN_HERE":
            hf_token = None

    model_config = ModelConfig(
        name=config_data["model"]["name"],
        hugging_face_token=hf_token,
        quantization=config_data.get("model", {}).get("quantization", "8bit"),
        session_cache=config_data.get("model", {}).get("session_cache", True),
    )

    output_config = OutputConfig(
        dir=Path(config_data["output"]["dir"]),
        filename_template=config_data["output"]["filename_template"],
    )

    templates_config = TemplatesConfig(
        dir=Path(config_data["templates"]["dir"]),
        doc_template=config_data["templates"]["doc_template"],
        style_guide=config_data["templates"]["style_guide"],
    )

    cache_config = CacheConfig(
        enabled=config_data.get("cache", {}).get("enabled", True),
        generation_cache=config_data.get("cache", {}).get("generation_cache", True),
        cache_dir=Path(
            config_data.get("cache", {}).get("cache_dir", ".cache/docgenai")
        ),
        max_cache_size_mb=config_data.get("cache", {}).get("max_cache_size_mb", 1000),
    )

    return AppConfig(
        model=model_config,
        output=output_config,
        templates=templates_config,
        cache=cache_config,
    )
