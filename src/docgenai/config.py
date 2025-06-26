# In this file, we will handle loading configuration from config.yaml
# and environment variables.

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    name: str
    hugging_face_token: str


@dataclass
class OutputConfig:
    dir: Path


@dataclass
class AppConfig:
    model: ModelConfig
    output: OutputConfig


def load_config(config_path: Path = None) -> "AppConfig":
    """
    Loads configuration from a YAML file, with environment variable overrides.
    """
    if config_path is None:
        config_path = Path("config.yaml")

    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

    # Allow environment variable overrides
    model_name = os.getenv("MODEL_NAME", config_data.get("model", {}).get("name"))
    hf_token = os.getenv(
        "HUGGING_FACE_TOKEN",
        config_data.get("model", {}).get("hugging_face_token"),
    )
    output_dir = os.getenv("OUTPUT_DIR", config_data.get("output", {}).get("dir"))

    if not all([model_name, hf_token, output_dir]):
        raise ValueError("Missing required configuration values.")

    return AppConfig(
        model=ModelConfig(name=model_name, hugging_face_token=hf_token),
        output=OutputConfig(dir=Path(output_dir)),
    )
