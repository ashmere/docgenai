import unittest
from pathlib import Path
from unittest.mock import patch

from docgenai.templates import TemplateLoader


class TestTemplateLoader(unittest.TestCase):
    def test_load_template_success(self):
        """Test successful loading of a template."""
        mock_template_dir = Path("/fake/dir")
        loader = TemplateLoader(template_dir=mock_template_dir)

        template_name = "test_template.md"
        template_content = "This is a test template."

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text") as mock_read_text:
                mock_read_text.return_value = template_content
                content = loader.load_template(template_name)
                self.assertEqual(content, template_content)
                mock_read_text.assert_called_once()

    def test_load_template_not_found(self):
        """Test FileNotFoundError when a template is not found."""
        mock_template_dir = Path("/fake/dir")
        loader = TemplateLoader(template_dir=mock_template_dir)

        template_name = "non_existent_template.md"

        with patch("pathlib.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                loader.load_template(template_name)

    def test_load_style_guide(self):
        """Test loading the default style guide."""
        loader = TemplateLoader()
        with patch.object(
            loader, "load_template", return_value="Style guide content"
        ) as mock_load:
            content = loader.load_style_guide()
            self.assertEqual(content, "Style guide content")
            mock_load.assert_called_once_with("default_style_guide.md")

    def test_load_doc_template(self):
        """Test loading the default doc template."""
        loader = TemplateLoader()
        with patch.object(
            loader, "load_template", return_value="Doc template content"
        ) as mock_load:
            content = loader.load_doc_template()
            self.assertEqual(content, "Doc template content")
            mock_load.assert_called_once_with("default_doc_template.md")

    def test_init_with_default_path(self):
        """Test that the default template path is correct."""
        loader = TemplateLoader()
        # Check that the path ends with the expected directory structure
        path_str = str(loader.template_dir)
        self.assertTrue(path_str.endswith("src/docgenai/templates"))


if __name__ == "__main__":
    unittest.main()
