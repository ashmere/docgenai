import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from docgenai.config import AppConfig, ModelConfig, OutputConfig
from docgenai.core import CoreProcessor


class TestCoreProcessor(unittest.TestCase):
    @patch("docgenai.core.load_config")
    @patch("docgenai.core.MMaDAModel")
    @patch("docgenai.core.TemplateLoader")
    def setUp(self, mock_template_loader, mock_mmada_model, mock_load_config):
        """Set up a CoreProcessor instance with mocked dependencies."""
        self.mock_config = AppConfig(
            model=ModelConfig(name="mmada", hugging_face_token="fake-token"),
            output=OutputConfig(dir=Path("test_output")),
        )
        mock_load_config.return_value = self.mock_config

        self.mock_model = MagicMock()
        mock_mmada_model.return_value = self.mock_model

        self.mock_template_loader = MagicMock()
        mock_template_loader.return_value = self.mock_template_loader

        self.processor = CoreProcessor()

    def test_process_delegates_to_process_file(self):
        """Test that process() delegates to process_file() for files."""
        file_path = MagicMock(spec=Path)
        file_path.is_dir.return_value = False
        file_path.is_file.return_value = True

        self.processor.process_file = MagicMock()
        self.processor.process_directory = MagicMock()

        self.processor.process(file_path)

        self.processor.process_file.assert_called_once_with(file_path)
        self.processor.process_directory.assert_not_called()

    def test_process_delegates_to_process_directory(self):
        """Test that process() delegates to process_directory() for directories."""
        dir_path = MagicMock(spec=Path)
        dir_path.is_dir.return_value = True
        dir_path.is_file.return_value = False

        self.processor.process_file = MagicMock()
        self.processor.process_directory = MagicMock()

        self.processor.process(dir_path)

        self.processor.process_directory.assert_called_once_with(dir_path)
        self.processor.process_file.assert_not_called()

    @patch("pathlib.Path.read_text", return_value="some code")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_process_file(self, mock_mkdir, mock_write_text, mock_read_text):
        """Test the orchestration within process_file."""
        self.mock_template_loader.load_documentation.return_value = "doc template"
        self.mock_template_loader.load_style_guide.return_value = "style guide"
        self.mock_model.analyze_code.return_value = "analysis"
        self.mock_model.generate_documentation.return_value = "generated doc"

        file_path = Path("source/test.py")
        result = self.processor.process_file(file_path)

        self.assertEqual(result, "test_output/test_doc.md")
        mock_read_text.assert_called_once()
        self.mock_model.analyze_code.assert_called_once_with("some code")
        self.mock_template_loader.load_documentation.assert_called_once()
        self.mock_template_loader.load_style_guide.assert_called_once()
        self.mock_model.generate_documentation.assert_called_once()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_text.assert_called_once_with("generated doc")

    @patch("docgenai.core.click.echo")
    @patch("pathlib.Path.rglob")
    def test_process_directory(self, mock_rglob, mock_echo):
        """Test that process_directory() processes all .py files found."""
        mock_dir_path = Path("fake_dir")
        mock_files = [Path("test1.py"), Path("test2.py")]
        mock_rglob.return_value = mock_files

        self.processor.process_file = MagicMock(return_value="processed")

        result = self.processor.process_directory(mock_dir_path)

        self.assertEqual(self.processor.process_file.call_count, 2)
        self.processor.process_file.assert_any_call(mock_files[0])
        self.processor.process_file.assert_any_call(mock_files[1])
        self.assertEqual(result, ["processed", "processed"])

    @patch("docgenai.core.click.echo")
    @patch("pathlib.Path.rglob")
    def test_process_directory_with_images(self, mock_rglob, mock_echo):
        """Test that process_directory() processes image files correctly."""
        mock_dir_path = Path("fake_dir")
        mock_files = [Path("test.png")]
        mock_rglob.return_value = mock_files

        self.processor.process_image = MagicMock(return_value="processed_image")

        result = self.processor.process_directory(mock_dir_path)

        self.processor.process_image.assert_called_once_with(mock_files[0])
        self.assertEqual(result, ["processed_image"])

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.read_text", return_value="code")
    def test_process_for_diagram(self, mock_read_text, mock_mkdir, mock_write_text):
        """Test the orchestration within process_for_diagram."""
        self.mock_model.generate_diagram.return_value = "diagram"

        file_path = Path("source/test.py")
        result = self.processor.process_for_diagram(file_path)

        self.assertEqual(result, "test_output/test_diagram.md")
        mock_read_text.assert_called_once()
        self.mock_model.generate_diagram.assert_called_once_with("code")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_text.assert_called_once_with("```mermaid\ndiagram\n```")


if __name__ == "__main__":
    unittest.main()
