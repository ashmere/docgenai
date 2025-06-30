import os
import sys
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

# Add src to path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from docgenai.config import (
    apply_env_overrides,
    create_default_config_file,
    get_cache_config,
    get_default_config,
    get_generation_config,
    get_model_config,
    get_output_config,
    load_config,
    merge_configs,
    validate_config,
)


class TestConfigLoading(unittest.TestCase):
    """Tests for configuration loading and management."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_config = {
            "model": {
                "mlx_model": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit",
                "transformers_model": "TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ",
                "temperature": 0.7,
                "max_tokens": 2048,
                "quantization": "4bit",
            },
            "cache": {
                "enabled": True,
                "generation_cache": True,
                "cache_dir": ".cache/docgenai",
                "max_cache_size_mb": 1000,
            },
            "output": {
                "dir": "output",
                "include_architecture": True,
                "include_code_stats": True,
            },
            "generation": {
                "file_patterns": ["*.py", "*.js"],
                "max_file_size_mb": 10,
                "skip_test_files": False,
            },
            "templates": {
                "dir": "templates",
                "doc_template": "default_doc_template.md",
            },
        }

    def test_get_default_config(self):
        """Test default configuration retrieval."""
        config = get_default_config()

        self.assertIsInstance(config, dict)
        self.assertIn("model", config)
        self.assertIn("cache", config)
        self.assertIn("output", config)
        self.assertIn("generation", config)
        self.assertIn("templates", config)
        self.assertIn("logging", config)

        # Check some default values
        self.assertIn("mlx_model", config["model"])
        self.assertIn("transformers_model", config["model"])
        self.assertEqual(config["cache"]["enabled"], True)
        self.assertEqual(config["output"]["dir"], "output")

    def test_merge_configs(self):
        """Test configuration merging."""
        base_config = {
            "model": {"temperature": 0.7, "max_tokens": 2048},
            "cache": {"enabled": True},
        }

        override_config = {
            "model": {"temperature": 0.5},  # Override existing
            "output": {"dir": "custom_output"},  # Add new section
        }

        merged = merge_configs(base_config, override_config)

        # Check merged values
        self.assertEqual(merged["model"]["temperature"], 0.5)  # Overridden
        self.assertEqual(merged["model"]["max_tokens"], 2048)  # Preserved
        self.assertEqual(merged["cache"]["enabled"], True)  # Preserved
        self.assertEqual(merged["output"]["dir"], "custom_output")  # Added

    def test_apply_env_overrides(self):
        """Test environment variable overrides."""
        config = {"model": {"temperature": 0.7}}

        # Mock environment variables
        with patch.dict(
            os.environ, {"DOCGENAI_MODEL__TEMPERATURE": "0.5"}, clear=False
        ):
            result = apply_env_overrides(config)
            # The implementation actually works and overrides the value
            self.assertEqual(
                result["model"]["temperature"], 0.5
            )  # Environment value takes precedence

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
model:
  temperature: 0.5
  max_tokens: 1024
cache:
  enabled: false
""",
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_config_from_file(self, mock_exists, mock_file):
        """Test loading configuration from YAML file."""
        config = load_config("test_config.yaml")

        self.assertIsInstance(config, dict)
        self.assertIn("model", config)
        self.assertEqual(config["model"]["temperature"], 0.5)
        self.assertEqual(config["model"]["max_tokens"], 1024)
        self.assertEqual(config["cache"]["enabled"], False)

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_config_file_not_found(self, mock_exists):
        """Test loading config when file doesn't exist."""
        config = load_config("nonexistent.yaml")

        # Should return default config
        self.assertIsInstance(config, dict)
        self.assertIn("model", config)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="invalid: yaml: content:",
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_config_yaml_error(self, mock_exists, mock_file):
        """Test handling of invalid YAML files."""
        # The implementation prints a warning but doesn't raise an exception
        config = load_config("invalid.yaml")

        # Should return default config when YAML is invalid
        self.assertIsInstance(config, dict)
        self.assertIn("model", config)

    def test_validate_config(self):
        """Test configuration validation."""
        invalid_config = {"model": {"temperature": "invalid"}}

        # Should raise TypeError when temperature is not a number
        with self.assertRaises(TypeError):
            validate_config(invalid_config)

    def test_get_model_config(self):
        """Test model configuration extraction."""
        config = get_model_config(self.sample_config)

        self.assertIsInstance(config, dict)
        self.assertIn("temperature", config)
        self.assertIn("max_tokens", config)
        self.assertEqual(config["temperature"], 0.7)

    def test_get_model_config_defaults(self):
        """Test model config extraction with defaults."""
        config = {}  # Empty config

        result = get_model_config(config)

        # Should return platform info even with empty config
        self.assertIn("is_mac", result)
        self.assertIn("platform", result)
        # temperature is not provided by default when section is missing
        self.assertNotIn("temperature", result)

    def test_get_cache_config(self):
        """Test cache config extraction."""
        config = {"cache": {"enabled": True, "max_size": 1000}}

        result = get_cache_config(config)

        self.assertEqual(result["enabled"], True)
        self.assertEqual(result["max_size"], 1000)

    def test_get_cache_config_defaults(self):
        """Test cache config with missing section."""
        config = {}  # No cache section

        result = get_cache_config(config)

        # Should return empty dict when section is missing
        self.assertEqual(result, {})

    def test_get_output_config(self):
        """Test output config extraction."""
        config = {"output": {"dir": "custom_output", "format": "markdown"}}

        result = get_output_config(config)

        self.assertEqual(result["dir"], "custom_output")
        self.assertEqual(result["format"], "markdown")

    def test_get_output_config_defaults(self):
        """Test output config with missing section."""
        config = {}  # No output section

        result = get_output_config(config)

        # Should return empty dict when section is missing
        self.assertEqual(result, {})

    def test_get_generation_config(self):
        """Test generation config extraction."""
        config = {"generation": {"max_workers": 8, "timeout": 300}}

        result = get_generation_config(config)

        self.assertEqual(result["max_workers"], 8)
        self.assertEqual(result["timeout"], 300)

    def test_get_generation_config_defaults(self):
        """Test generation config with missing section."""
        config = {}  # No generation section

        result = get_generation_config(config)

        # Should return empty dict when section is missing
        self.assertEqual(result, {})

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.write_text")
    def test_create_default_config_file(self, mock_write, mock_file):
        """Test creating default configuration file."""
        with patch("pathlib.Path.exists", return_value=False):
            result_path = create_default_config_file("test_config.yaml")

            self.assertIsInstance(result_path, Path)
            self.assertEqual(str(result_path), "test_config.yaml")

    def test_config_merging_deep(self):
        """Test deep merging of nested configuration."""
        base = {
            "model": {"temperature": 0.7, "max_tokens": 2048, "nested": {"value": 1}}
        }

        override = {
            "model": {"temperature": 0.5, "nested": {"value": 2, "new_key": "test"}}
        }

        result = merge_configs(base, override)

        self.assertEqual(result["model"]["temperature"], 0.5)
        self.assertEqual(result["model"]["max_tokens"], 2048)
        self.assertEqual(result["model"]["nested"]["value"], 2)
        self.assertEqual(result["model"]["nested"]["new_key"], "test")

    def test_environment_variable_conversion(self):
        """Test environment variable type conversion."""
        config = {"test": {}}

        with patch.dict(
            os.environ,
            {
                "DOCGENAI_TEST__STR_VAL": "hello",
                "DOCGENAI_TEST__INT_VAL": "42",
                "DOCGENAI_TEST__FLOAT_VAL": "3.14",
                "DOCGENAI_TEST__BOOL_VAL": "true",
                "DOCGENAI_TEST__LIST_VAL": "a,b,c",
            },
        ):
            result = apply_env_overrides(config)

            # Check that values are converted correctly
            self.assertEqual(result["test"]["str_val"], "hello")
            self.assertEqual(result["test"]["int_val"], 42)
            self.assertEqual(result["test"]["float_val"], 3.14)
            self.assertEqual(
                result["test"]["bool_val"], True
            )  # Implementation returns True
            self.assertEqual(result["test"]["list_val"], ["a", "b", "c"])

    def test_config_file_precedence(self):
        """Test configuration file precedence over defaults."""
        file_config = """
model:
  temperature: 0.3
  custom_setting: true
"""

        with patch("builtins.open", mock_open(read_data=file_config)):
            with patch("pathlib.Path.exists", return_value=True):
                config = load_config("test.yaml")

                # File values should override defaults
                self.assertEqual(config["model"]["temperature"], 0.3)
                self.assertTrue(config["model"]["custom_setting"])

                # Default values should still be present
                self.assertIn("max_tokens", config["model"])


class TestConfigUtilities(unittest.TestCase):
    """Tests for configuration utility functions."""

    def test_config_section_extraction(self):
        """Test extracting configuration sections."""
        full_config = get_default_config()

        # Test each section extraction function
        model_config = get_model_config(full_config)
        cache_config = get_cache_config(full_config)
        output_config = get_output_config(full_config)
        generation_config = get_generation_config(full_config)

        # Each should be a dict with expected keys
        self.assertIsInstance(model_config, dict)
        self.assertIsInstance(cache_config, dict)
        self.assertIsInstance(output_config, dict)
        self.assertIsInstance(generation_config, dict)

        # Check for expected keys in each section
        self.assertIn("temperature", model_config)
        self.assertIn("enabled", cache_config)
        self.assertIn("dir", output_config)
        self.assertIn("file_patterns", generation_config)

    def test_config_validation_with_missing_sections(self):
        """Test validation with incomplete configuration."""
        partial_config = {"model": {"temperature": 0.5}}

        validated = validate_config(partial_config)

        # Should return the original config without adding missing sections
        self.assertIn("model", validated)
        self.assertEqual(validated["model"]["temperature"], 0.5)
        # Missing sections are not automatically added
        self.assertNotIn("cache", validated)


if __name__ == "__main__":
    unittest.main()
