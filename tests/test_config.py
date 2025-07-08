"""
Test configuration loading and validation.

These tests don't require model downloads or external dependencies.
"""

import sys
from pathlib import Path

import pytest
import yaml

# Import the config module
sys.path.insert(0, "src")
from docgenai.config import load_config  # noqa: E402


class TestConfig:
    """Test configuration loading and validation."""

    @pytest.mark.unit
    def test_default_config_loading(self):
        """Test that default configuration can be loaded."""
        config = load_config()

        # Verify basic structure exists
        assert "model" in config
        assert "cache" in config
        assert "output" in config
        assert "file_selection" in config

        # Verify model configuration
        model_config = config["model"]
        assert "mlx_model" in model_config
        assert "transformers_model" in model_config
        assert "temperature" in model_config

        # Verify cache configuration
        cache_config = config["cache"]
        assert "enabled" in cache_config
        assert "cache_dir" in cache_config

    @pytest.mark.unit
    def test_config_file_exists(self):
        """Test that the main config file exists."""
        config_path = Path("config.yaml")
        assert config_path.exists(), "config.yaml should exist in project root"

        # Test that it's valid YAML
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        assert isinstance(config_data, dict), "Config should be a dictionary"

    @pytest.mark.unit
    def test_config_required_sections(self):
        """Test that all required configuration sections exist."""
        config = load_config()

        required_sections = [
            "model",
            "cache",
            "output",
            "file_selection",
            "chunking",
            "chains",
            "templates",
            "generation",
            "logging",
            "performance",
        ]

        for section in required_sections:
            assert (
                section in config
            ), f"Required section '{section}' missing from config"

    @pytest.mark.unit
    def test_model_config_structure(self):
        """Test model configuration structure."""
        config = load_config()
        model_config = config["model"]

        # Required model fields
        required_fields = [
            "mlx_model",
            "transformers_model",
            "temperature",
            "max_tokens",
        ]

        for field in required_fields:
            assert field in model_config, f"Required model field '{field}' missing"

        # Validate types
        assert isinstance(model_config["temperature"], (int, float))
        assert isinstance(model_config["max_tokens"], int)
        assert model_config["temperature"] >= 0.0
        assert model_config["max_tokens"] > 0

    @pytest.mark.unit
    def test_file_selection_patterns(self):
        """Test file selection configuration."""
        config = load_config()
        file_config = config["file_selection"]

        assert "include_patterns" in file_config
        assert "exclude_patterns" in file_config
        assert isinstance(file_config["include_patterns"], list)
        assert isinstance(file_config["exclude_patterns"], list)

        # Should include Python files
        assert "*.py" in file_config["include_patterns"]

        # Should exclude common build/cache directories
        exclude_patterns = file_config["exclude_patterns"]
        assert any("__pycache__" in pattern for pattern in exclude_patterns)
        assert any("node_modules" in pattern for pattern in exclude_patterns)

    @pytest.mark.unit
    def test_cache_config_validation(self):
        """Test cache configuration validation."""
        config = load_config()
        cache_config = config["cache"]

        # Required cache fields
        required_fields = ["enabled", "cache_dir", "max_cache_size_mb"]
        for field in required_fields:
            assert field in cache_config, f"Required cache field '{field}' missing"

        # Validate types
        assert isinstance(cache_config["enabled"], bool)
        assert isinstance(cache_config["max_cache_size_mb"], int)
        assert cache_config["max_cache_size_mb"] > 0

    @pytest.mark.unit
    def test_output_config_validation(self):
        """Test output configuration validation."""
        config = load_config()
        output_config = config["output"]

        required_fields = ["dir", "filename_template", "include_architecture"]
        for field in required_fields:
            assert field in output_config, f"Required output field '{field}' missing"

        # Validate filename template has placeholder
        template = output_config["filename_template"]
        assert (
            "{name}" in template
        ), "Filename template should contain {name} placeholder"

    @pytest.mark.unit
    def test_logging_config_validation(self):
        """Test logging configuration validation."""
        config = load_config()
        logging_config = config["logging"]

        required_fields = ["level", "format", "console"]
        for field in required_fields:
            assert field in logging_config, f"Required logging field '{field}' missing"

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert (
            logging_config["level"] in valid_levels
        ), f"Invalid log level: {logging_config['level']}"
