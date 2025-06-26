import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import yaml

from docgenai.config import AppConfig, load_config


class TestConfig(unittest.TestCase):
    """
    Tests for the configuration loading logic.
    """

    def setUp(self):
        """Create a dummy config file for tests."""
        self.test_config_path = Path("test_config.yaml")
        self.dummy_config = {
            "model": {"name": "test-model"},
            "output": {"dir": "test-output"},
        }
        with open(self.test_config_path, "w") as f:
            yaml.dump(self.dummy_config, f)

    def tearDown(self):
        """Remove the dummy config file."""
        if self.test_config_path.exists():
            self.test_config_path.unlink()

    @patch("os.getenv")
    @patch("pathlib.Path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
    model:
      name: "default-model"
      hugging_face_token: "default-token"
    output:
      dir: "default/output"
    """,
    )
    def test_load_config_success_from_file(self, mock_file, mock_exists, mock_getenv):
        """Test successful config loading from a YAML file."""
        mock_exists.return_value = True
        # Let getenv return the default value (None)
        mock_getenv.side_effect = lambda key, default=None: default

        config = load_config(Path("dummy/path/config.yaml"))

        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.model.name, "default-model")
        self.assertEqual(config.model.hugging_face_token, "default-token")
        self.assertEqual(config.output.dir, Path("default/output"))

    @patch("os.getenv")
    def test_load_config_success_from_env(self, mock_getenv):
        """Test successful config loading using environment variables."""
        # Mock os.getenv to return specific values
        env_vars = {
            "MODEL_NAME": "env-model",
            "HUGGING_FACE_TOKEN": "env-token",
            "OUTPUT_DIR": "env/output",
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)

        # We can pass a non-existent file path since env vars will be used
        with patch("pathlib.Path.exists", return_value=False):
            # We need to mock open so it doesn't fail
            with patch("builtins.open", mock_open(read_data="{}")):
                # The function will still try to load the default config.yaml
                # so we need to ensure all required values are in env
                config = load_config()

        self.assertEqual(config.model.name, "env-model")
        self.assertEqual(config.model.hugging_face_token, "env-token")
        self.assertEqual(config.output.dir, Path("env/output"))

    @patch("pathlib.Path.exists", return_value=False)
    @patch("os.getenv", return_value=None)
    def test_load_config_raises_on_no_config(self, mock_getenv, mock_exists):
        """
        Test ValueError when no config file or env vars are found.
        """
        with self.assertRaises(ValueError):
            load_config()

    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("os.getenv", return_value=None)
    def test_load_config_missing_values(self, mock_getenv, mock_file, mock_exists):
        """Test ValueError when required configuration is missing."""
        with self.assertRaises(ValueError):
            load_config()


if __name__ == "__main__":
    unittest.main()
