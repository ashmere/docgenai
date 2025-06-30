"""
Configuration management for DocGenAI.

Handles loading configuration from YAML files, environment variables,
and provides sensible defaults for all settings with comprehensive
support for the new DeepSeek-Coder models and platform-aware settings.
"""

import os
import platform
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration with platform-aware settings."""

    return {
        "model": {
            # Platform-aware model selection
            "mlx_model": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit",
            "transformers_model": "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
            # Generation parameters
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.8,
            "top_k": 50,
            "do_sample": True,
            # Quantization settings (non-MLX platforms)
            "quantization": "4bit",
            # Model caching
            "session_cache": True,
            "cache_model_files": True,
            # Hardware optimization
            "device_map": "auto",
            "torch_dtype": "auto",
            "trust_remote_code": True,
        },
        "cache": {
            "enabled": True,
            "generation_cache": True,
            "model_cache": True,
            "cache_dir": ".cache/docgenai",
            "model_cache_dir": ".cache/models",
            "max_cache_size_mb": 2000,
            "max_generation_cache_mb": 500,
            "max_model_cache_mb": 1500,
            "generation_ttl_hours": 24,
            "model_ttl_hours": 168,
            "auto_cleanup": True,
            "cleanup_on_startup": False,
        },
        "output": {
            "dir": "output",
            "filename_template": "{name}_documentation.md",
            "include_architecture": True,
            "include_code_stats": True,
            "include_dependencies": True,
            "include_examples": True,
            "include_diagrams": False,
            "create_subdirs": True,
            "preserve_structure": True,
            "markdown_style": "github",
            "code_block_language": "auto",
            "table_format": "github",
        },
        "templates": {
            "dir": "src/docgenai/templates",
            "doc_template": "default_doc_template.md",
            "style_guide": "default_style_guide.md",
            "summary_template": "directory_summary.md",
            "footer_template": "default_footer.md",
            "extended_footer_template": "default_extended_footer.md",
            "use_extended_footer": False,
            "custom_templates_dir": "templates",
            "allow_custom_templates": True,
            "author": "",
            "organization": "",
            "project_name": "",
            "version": "1.0.0",
        },
        "generation": {
            "file_patterns": [
                "*.py",
                "*.js",
                "*.ts",
                "*.jsx",
                "*.tsx",
                "*.cpp",
                "*.cc",
                "*.cxx",
                "*.c",
                "*.h",
                "*.hpp",
                "*.java",
                "*.go",
                "*.rs",
                "*.rb",
                "*.php",
                "*.cs",
                "*.swift",
                "*.kt",
                "*.scala",
                "*.r",
                "*.R",
            ],
            "max_file_size_mb": 10,
            "skip_binary_files": True,
            "skip_generated_files": True,
            "skip_test_files": False,
            "max_workers": 4,
            "batch_size": 5,
            "analyze_imports": True,
            "analyze_functions": True,
            "analyze_classes": True,
            "analyze_complexity": True,
            "detail_level": "medium",
            "include_private_methods": False,
            "include_internal_classes": False,
        },
        "logging": {
            "level": "INFO",
            "verbose_level": "DEBUG",
            "format": "%(message)s",
            "verbose_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "console": True,
            "file": False,
            "log_file": "logs/docgenai.log",
            "max_log_size_mb": 10,
            "backup_count": 3,
        },
        "security": {
            "allow_remote_code": True,
            "verify_ssl": True,
            "restrict_file_access": False,
            "allowed_directories": [],
            "proxy_url": "",
            "timeout_seconds": 300,
        },
        "performance": {
            "max_memory_usage_gb": 16,
            "memory_cleanup_threshold": 0.8,
            "max_concurrent_files": 10,
            "processing_timeout_minutes": 30,
            "use_cpu_offload": False,
            "use_disk_offload": False,
            "optimize_for_speed": True,
            "auto_detect_gpu": True,
            "prefer_gpu": True,
        },
        "integrations": {
            "git": {
                "enabled": True,
                "include_commit_info": True,
                "include_branch_info": True,
                "include_author_info": False,
            },
            "vscode": {"enabled": False, "config_path": ".vscode/settings.json"},
            "github_actions": {
                "enabled": False,
                "workflow_path": ".github/workflows/docs.yml",
            },
            "gitbook": {"enabled": False, "api_key": ""},
            "confluence": {"enabled": False, "base_url": "", "api_key": ""},
        },
        "experimental": {
            "interactive_mode": False,
            "ai_suggestions": False,
            "code_refactoring_hints": False,
            "documentation_scoring": False,
            "auto_update_docs": False,
            "multi_model_consensus": False,
            "custom_prompt_engineering": False,
            "domain_specific_training": False,
        },
    }


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge configuration dictionaries.

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary

    Returns:
        Merged configuration dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.

    Environment variables should be prefixed with DOCGENAI_ and use
    double underscores to separate nested keys.

    Example: DOCGENAI_MODEL__TEMPERATURE=0.8
    Example: DOCGENAI_CACHE__ENABLED=false
    Example: DOCGENAI_OUTPUT__DIR=/custom/output

    Args:
        config: Configuration dictionary to override

    Returns:
        Configuration with environment overrides applied
    """
    env_prefix = "DOCGENAI_"

    for env_key, env_value in os.environ.items():
        if not env_key.startswith(env_prefix):
            continue

        # Remove prefix and split on double underscores
        config_path = env_key[len(env_prefix) :].split("__")

        # Navigate to the correct nested location
        current_config = config
        for key in config_path[:-1]:
            key = key.lower()
            if key not in current_config:
                current_config[key] = {}
            current_config = current_config[key]

        # Set the final value (convert common types)
        final_key = config_path[-1].lower()
        converted_value = _convert_env_value(env_value)
        current_config[final_key] = converted_value

    return config


def _convert_env_value(env_value: str) -> Any:
    """Convert environment variable string to appropriate type."""
    # Boolean conversion
    if env_value.lower() in ("true", "false"):
        return env_value.lower() == "true"

    # Integer conversion
    if env_value.isdigit() or (env_value.startswith("-") and env_value[1:].isdigit()):
        return int(env_value)

    # Float conversion
    try:
        if "." in env_value:
            return float(env_value)
    except ValueError:
        pass

    # List conversion (comma-separated)
    if "," in env_value:
        return [item.strip() for item in env_value.split(",")]

    # Return as string
    return env_value


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration with hierarchy: defaults -> file -> environment.

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        Complete configuration dictionary
    """
    # Start with defaults
    config = get_default_config()

    # Override with file config if provided
    if config_path:
        config_file = Path(config_path)
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    file_config = yaml.safe_load(f) or {}
                config = merge_configs(config, file_config)
            except (yaml.YAMLError, IOError) as e:
                # Log warning but continue with defaults
                print(f"Warning: Could not load config file {config_path}: {e}")
    else:
        # Try to load default config.yaml if it exists
        default_config_path = Path("config.yaml")
        if default_config_path.exists():
            try:
                with open(default_config_path, "r", encoding="utf-8") as f:
                    file_config = yaml.safe_load(f) or {}
                config = merge_configs(config, file_config)
            except (yaml.YAMLError, IOError):
                # Silently continue with defaults
                pass

    # Apply environment variable overrides
    config = apply_env_overrides(config)

    # Validate and normalize the configuration
    config = validate_config(config)

    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize configuration values.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Validated configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate model settings
    model_config = config.get("model", {})

    temperature = model_config.get("temperature", 0.7)
    if not (0.0 <= temperature <= 2.0):
        raise ValueError(
            f"Model temperature must be between 0.0 and 2.0, got {temperature}"
        )

    max_tokens = model_config.get("max_tokens", 2048)
    if not (1 <= max_tokens <= 8192):
        raise ValueError(
            f"Model max_tokens must be between 1 and 8192, got {max_tokens}"
        )

    top_p = model_config.get("top_p", 0.8)
    if not (0.0 <= top_p <= 1.0):
        raise ValueError(f"Model top_p must be between 0.0 and 1.0, got {top_p}")

    top_k = model_config.get("top_k", 50)
    if not (1 <= top_k <= 100):
        raise ValueError(f"Model top_k must be between 1 and 100, got {top_k}")

    # Validate cache settings
    cache_config = config.get("cache", {})

    max_cache_size = cache_config.get("max_cache_size_mb", 2000)
    if max_cache_size < 0:
        raise ValueError(
            f"Cache max_cache_size_mb must be non-negative, got {max_cache_size}"
        )

    # Validate performance settings
    performance_config = config.get("performance", {})

    max_memory = performance_config.get("max_memory_usage_gb", 16)
    if max_memory <= 0:
        raise ValueError(
            f"Performance max_memory_usage_gb must be positive, got {max_memory}"
        )

    max_workers = config.get("generation", {}).get("max_workers", 4)
    if max_workers <= 0:
        raise ValueError(f"Generation max_workers must be positive, got {max_workers}")

    # Ensure required directories exist in config
    output_dir = Path(config.get("output", {}).get("dir", "output"))
    cache_dir = Path(config.get("cache", {}).get("cache_dir", ".cache/docgenai"))

    # Create directories if they don't exist
    for directory in [output_dir, cache_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    return config


def get_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and prepare model-specific configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Model configuration dictionary
    """
    model_config = config.get("model", {})

    # Add platform detection
    is_mac = platform.system() == "Darwin"
    model_config["is_mac"] = is_mac
    model_config["platform"] = platform.system()

    return model_config


def get_cache_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract cache configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Cache configuration dictionary
    """
    return config.get("cache", {})


def get_output_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract output configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Output configuration dictionary
    """
    return config.get("output", {})


def get_generation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract generation configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Generation configuration dictionary
    """
    return config.get("generation", {})


def create_default_config_file(path: str = "config.yaml") -> Path:
    """
    Create a default configuration file with comprehensive settings.

    Args:
        path: Path where to create the config file

    Returns:
        Path to the created config file
    """
    config_path = Path(path)

    # Don't overwrite existing config
    if config_path.exists():
        return config_path

    # Get default config and save to YAML
    default_config = get_default_config()

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(
            default_config, f, default_flow_style=False, indent=2, sort_keys=False
        )

    return config_path


def load_model_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration and return model-specific settings.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Model configuration dictionary
    """
    config = load_config(str(config_path) if config_path else None)
    return get_model_config(config)
