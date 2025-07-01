import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from docgenai.models import AIModel, DeepSeekCoderModel, create_model


class TestDeepSeekCoderModel(unittest.TestCase):
    """
    Tests for the DeepSeekCoderModel class.
    Uses mocking to avoid loading actual models during testing.
    """

    def setUp(self):
        """Set up test configuration."""
        self.test_config = {
            "model": {
                "mlx_model": ("mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit"),
                "transformers_model": (
                    "TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ"
                ),
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.8,
                "top_k": 50,
                "do_sample": True,
                "quantization": "4bit",
                "device_map": "auto",
                "torch_dtype": "auto",
                "trust_remote_code": True,
            }
        }

    @patch("docgenai.models.platform.system")
    def test_platform_detection_darwin(self, mock_system):
        """Test platform detection for macOS."""
        mock_system.return_value = "Darwin"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)

            self.assertEqual(model.platform, "Darwin")
            self.assertTrue(model.is_mac)
            self.assertEqual(model.backend, "mlx")
            self.assertEqual(
                model.model_path, "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit"
            )

    @patch("docgenai.models.platform.system")
    def test_platform_detection_linux(self, mock_system):
        """Test platform detection for Linux."""
        mock_system.return_value = "Linux"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)

            self.assertEqual(model.platform, "Linux")
            self.assertFalse(model.is_mac)
            self.assertEqual(model.backend, "transformers")
            self.assertEqual(
                model.model_path, "TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ"
            )

    @patch("docgenai.models.platform.system")
    def test_model_initialization_parameters(self, mock_system):
        """Test that model parameters are set correctly from config."""
        mock_system.return_value = "Darwin"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)

            self.assertEqual(model.temperature, 0.7)
            self.assertEqual(model.max_tokens, 2048)
            self.assertEqual(model.top_p, 0.8)
            self.assertEqual(model.top_k, 50)
            self.assertTrue(model.do_sample)
            self.assertEqual(model.quantization, "4bit")

    @patch("docgenai.models.platform.system")
    def test_mlx_model_initialization(self, mock_system):
        """Test MLX model initialization for macOS."""
        mock_system.return_value = "Darwin"

        mock_mlx_load = Mock()
        mock_mlx_generate = Mock()
        mock_model = Mock()
        mock_tokenizer = Mock()

        mock_mlx_load.return_value = (mock_model, mock_tokenizer)

        with patch(
            "docgenai.models.DeepSeekCoderModel._initialize_mlx_model"
        ) as mock_init:
            model = DeepSeekCoderModel(self.test_config)
            mock_init.assert_called_once()

    @patch("docgenai.models.platform.system")
    def test_transformers_model_initialization(self, mock_system):
        """Test transformers model initialization for non-macOS."""
        mock_system.return_value = "Linux"

        with patch(
            "docgenai.models.DeepSeekCoderModel._initialize_transformers_model"
        ) as mock_init:
            model = DeepSeekCoderModel(self.test_config)
            mock_init.assert_called_once()

    @patch("docgenai.models.platform.system")
    def test_generate_documentation(self, mock_system):
        """Test documentation generation."""
        mock_system.return_value = "Darwin"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)

            # Mock the text generation method
            with patch.object(model, "_generate_text") as mock_generate:
                mock_generate.return_value = "Generated documentation content"

                code = "def test_function(): pass"
                file_path = "test.py"

                result = model.generate_documentation(code, file_path)

                self.assertIsInstance(result, str)
                mock_generate.assert_called()

    @patch("docgenai.models.platform.system")
    def test_generate_architecture_description(self, mock_system):
        """Test architecture description generation."""
        mock_system.return_value = "Darwin"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)

            # Mock the text generation method
            with patch.object(model, "_generate_text") as mock_generate:
                mock_generate.return_value = "Generated architecture description"

                code = "class TestClass: pass"
                file_path = "test.py"

                result = model.generate_architecture_description(code, file_path)

                self.assertIsInstance(result, str)
                mock_generate.assert_called()

    @patch("docgenai.models.platform.system")
    def test_is_available(self, mock_system):
        """Test model availability check."""
        mock_system.return_value = "Darwin"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)
            model.model = Mock()  # Simulate loaded model
            model.tokenizer = Mock()  # Simulate loaded tokenizer

            self.assertTrue(model.is_available())

            # Test when model is not loaded
            model.model = None
            self.assertFalse(model.is_available())

    @patch("docgenai.models.platform.system")
    def test_get_model_info(self, mock_system):
        """Test model info retrieval."""
        mock_system.return_value = "Darwin"

        with patch("docgenai.models.DeepSeekCoderModel._initialize_model"):
            model = DeepSeekCoderModel(self.test_config)

            info = model.get_model_info()

            self.assertIsInstance(info, dict)
            self.assertIn("model_path", info)
            self.assertIn("backend", info)
            self.assertIn("platform", info)
            self.assertIn("temperature", info)
            self.assertIn("max_tokens", info)
            self.assertIn("quantization", info)
            self.assertIn("available", info)

            self.assertEqual(
                info["model_path"], "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit"
            )
            self.assertEqual(info["backend"], "mlx")
            self.assertEqual(info["platform"], "Darwin")


class TestCreateModel(unittest.TestCase):
    """Tests for the create_model factory function."""

    @patch("docgenai.models.DeepSeekCoderModel")
    def test_create_model_with_config(self, mock_model_class):
        """Test model creation with configuration."""
        mock_instance = Mock()
        mock_model_class.return_value = mock_instance

        config = {"model": {"temperature": 0.5}}
        result = create_model(config)

        mock_model_class.assert_called_once_with(config)
        self.assertEqual(result, mock_instance)

    @patch("docgenai.models.DeepSeekCoderModel")
    def test_create_model_without_config(self, mock_model_class):
        """Test model creation without configuration."""
        mock_instance = Mock()
        mock_model_class.return_value = mock_instance

        result = create_model()

        mock_model_class.assert_called_once_with(None)
        self.assertEqual(result, mock_instance)

    @patch("docgenai.models.DeepSeekCoderModel")
    def test_create_model_error_handling(self, mock_model_class):
        """Test error handling in model creation."""
        mock_model_class.side_effect = Exception("Model initialization failed")

        with self.assertRaises(Exception) as context:
            create_model()

        self.assertIn("Model initialization failed", str(context.exception))


class TestAIModelInterface(unittest.TestCase):
    """Tests for the AIModel abstract base class."""

    def test_abstract_methods(self):
        """Test that AIModel cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            AIModel()

    def test_concrete_implementation(self):
        """Test that DeepSeekCoderModel properly implements AIModel interface."""
        # Check that DeepSeekCoderModel is a subclass of AIModel
        self.assertTrue(issubclass(DeepSeekCoderModel, AIModel))

        # Check that all abstract methods are implemented
        abstract_methods = AIModel.__abstractmethods__
        for method_name in abstract_methods:
            self.assertTrue(hasattr(DeepSeekCoderModel, method_name))


if __name__ == "__main__":
    unittest.main()
