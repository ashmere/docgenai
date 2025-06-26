import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from docgenai.core import CoreProcessor


class TestCoreProcessor(unittest.TestCase):
    @patch("docgenai.core.load_config")
    @patch("docgenai.core.MMaDAModel")
    @patch("docgenai.core.TemplateLoader")
    def setUp(self, mock_template_loader, mock_mmada_model, mock_load_config):
        """Set up a CoreProcessor instance with mocked dependencies."""
        self.mock_config = MagicMock()
        mock_load_config.return_value = self.mock_config
        self.mock_config.model.name = "mmada"

        self.mock_model = MagicMock()
        mock_mmada_model.return_value = self.mock_model

        self.mock_templates = MagicMock()
        mock_template_loader.return_value = self.mock_templates

        self.processor = CoreProcessor()

    def test_init(self):
        """Test that the processor initializes its components correctly."""
        self.assertIsNotNone(self.processor.config)
        self.assertIsNotNone(self.processor.ai_model)
        self.assertIsNotNone(self.processor.template_loader)
        self.assertEqual(self.processor.ai_model, self.mock_model)

    @patch("pathlib.Path.is_file", return_value=True)
    def test_process_dispatches_to_file(self, mock_is_file):
        """Test that process() calls process_file() for a file path."""
        with patch.object(self.processor, "process_file") as mock_process_file:
            test_path = Path("fake/file.py")
            self.processor.process(test_path)
            mock_process_file.assert_called_once_with(test_path)

    @patch("pathlib.Path.is_file", return_value=False)
    @patch("pathlib.Path.is_dir", return_value=True)
    def test_process_dispatches_to_directory(self, mock_is_dir, mock_is_file):
        """Test that process() calls process_directory() for a directory."""
        with patch.object(self.processor, "process_directory") as mock_process_dir:
            test_path = Path("fake/dir")
            self.processor.process(test_path)
            mock_process_dir.assert_called_once_with(test_path)

    @patch("pathlib.Path.is_file", return_value=False)
    @patch("pathlib.Path.is_dir", return_value=False)
    def test_process_raises_for_invalid_path(self, mock_is_dir, mock_is_file):
        """Test that process() raises FileNotFoundError for a bad path."""
        with self.assertRaises(FileNotFoundError):
            self.processor.process(Path("non/existent/path"))

    @patch("pathlib.Path.read_text", return_value="some code")
    def test_process_file_orchestration(self, mock_read_text):
        """Test the orchestration within process_file."""
        self.mock_model.analyze_code.return_value = "analysis"
        self.mock_model.generate_documentation.return_value = "doc"
        self.mock_templates.load_doc_template.return_value = "doc temp"
        self.mock_templates.load_style_guide.return_value = "style"

        result = self.processor.process_file(Path("fake/file.py"))

        self.assertEqual(result, "doc")
        mock_read_text.assert_called_once()
        self.mock_model.analyze_code.assert_called_once_with("some code")
        self.mock_templates.load_doc_template.assert_called_once()
        self.mock_templates.load_style_guide.assert_called_once()
        self.mock_model.generate_documentation.assert_called_once()


if __name__ == "__main__":
    unittest.main()
