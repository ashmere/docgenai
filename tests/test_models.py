import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from PIL import Image

# This is a common pattern for making the 'src' directory importable in tests.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from docgenai.models import MMaDAModel


class TestMMaDAModel(unittest.TestCase):
    """
    Tests for the MMaDAModel class.
    It uses mocking to avoid loading the actual Hugging Face model.
    """

    @patch("docgenai.models.pipeline")
    def test_text_generation(self, mock_pipeline):
        """
        Test that generate_text calls the text generation pipeline correctly.
        """
        # Arrange
        mock_text_generator = MagicMock()
        mock_text_generator.return_value = [{"generated_text": "This is a test."}]
        mock_pipeline.return_value = mock_text_generator

        model = MMaDAModel()
        prompt = "Explain this code"

        # Act
        result = model.generate_text(prompt)

        # Assert
        mock_pipeline.assert_called_once_with(
            "text-generation",
            model="Gen-Verse/MMaDA-8B-Base",
            torch_dtype=unittest.mock.ANY,
            trust_remote_code=True,
        )
        model.text_pipeline.assert_called_once_with(prompt, max_length=512)
        self.assertEqual(result, "This is a test.")

    def test_image_generation_placeholder(self):
        """
        Test the placeholder image generation.
        """
        # Arrange
        model = MMaDAModel()
        prompt = "Create a diagram"

        # Act
        result = model.generate_image(prompt)

        # Assert
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (512, 512))


if __name__ == "__main__":
    unittest.main()
