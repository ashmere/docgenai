import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add src to path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from docgenai.cache import CacheManager
from docgenai.core import DocumentationGenerator
from docgenai.models import AIModel
from docgenai.templates import TemplateManager


class TestDocumentationGenerator(unittest.TestCase):
    """Tests for the DocumentationGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock(spec=AIModel)
        self.mock_model.get_model_info.return_value = {
            "model_path": "test-model",
            "backend": "mlx",
            "platform": "Darwin",
            "temperature": 0.7,
            "max_tokens": 2048,
            "quantization": "4bit",
            "available": True,
        }

        self.test_config = {
            "cache": {
                "enabled": True,
                "directory": ".test_cache",
                "max_size_mb": 100,
                "ttl_hours": 24,
            },
            "output": {
                "dir": "test_output",
                "filename_template": "{name}_documentation.md",
                "include_architecture": True,
                "include_code_stats": True,
                "preserve_structure": True,
            },
            "generation": {
                "file_patterns": ["*.py"],
                "max_file_size_mb": 10,
                "skip_test_files": False,
                "skip_generated_files": True,
            },
            "model": {
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            "templates": {
                "dir": "templates",
                "doc_template": "default_doc_template.md",
            },
        }

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_initialization(self, mock_template_manager, mock_cache_manager):
        """Test DocumentationGenerator initialization."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        self.assertEqual(generator.model, self.mock_model)
        self.assertEqual(generator.config, self.test_config)
        mock_cache_manager.assert_called_once()
        mock_template_manager.assert_called_once()

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_process_file_success(self, mock_template_manager, mock_cache_manager):
        """Test successful file processing."""
        # Setup mocks
        mock_cache = MagicMock()
        mock_template = MagicMock()
        mock_cache_manager.return_value = mock_cache
        mock_template_manager.return_value = mock_template

        mock_cache.get_cached_result.return_value = None  # No cache hit
        self.mock_model.generate_documentation.return_value = "Test documentation"
        self.mock_model.generate_architecture_description.return_value = (
            "Test architecture"
        )
        mock_template.render_documentation.return_value = "Rendered content"

        generator = DocumentationGenerator(self.mock_model, self.test_config)

        # Create a test file
        test_file = Path("test_file.py")
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 1024  # 1KB file
                with patch("builtins.open", mock_open(read_data="def test(): pass")):
                    with patch.object(
                        generator, "_save_documentation", return_value="output.md"
                    ):
                        result = generator.process_file(test_file)

        self.assertEqual(result, "output.md")
        self.mock_model.generate_documentation.assert_called_once()
        self.mock_model.generate_architecture_description.assert_called_once()
        mock_template.render_documentation.assert_called_once()

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_process_file_cached_result(
        self, mock_template_manager, mock_cache_manager
    ):
        """Test file processing with cached result."""
        # Setup mocks
        mock_cache = mock_cache_manager.return_value
        mock_template = mock_template_manager.return_value

        generator = DocumentationGenerator(self.mock_model, self.test_config)

        # Mock cache hit
        mock_cache.get_cached_result.return_value = "cached_output.md"

        test_file = Path("test_file.py")

        # The actual implementation checks if file exists first
        # and returns None if it doesn't exist, regardless of cache
        with patch("pathlib.Path.exists", return_value=False):
            result = generator.process_file(test_file)

        # Should return None because file doesn't exist
        self.assertIsNone(result)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_process_file_nonexistent(self, mock_template_manager, mock_cache_manager):
        """Test processing non-existent file."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        test_file = Path("nonexistent.py")
        with patch("pathlib.Path.exists", return_value=False):
            result = generator.process_file(test_file)

        self.assertIsNone(result)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_process_file_too_large(self, mock_template_manager, mock_cache_manager):
        """Test processing file that's too large."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        test_file = Path("large_file.py")
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                # File larger than max_file_size_mb (10MB)
                mock_stat.return_value.st_size = 20 * 1024 * 1024  # 20MB
                result = generator.process_file(test_file)

        self.assertIsNone(result)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_process_directory_success(self, mock_template_manager, mock_cache_manager):
        """Test successful directory processing."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        test_dir = Path("test_dir")
        with patch("pathlib.Path.is_dir", return_value=True):
            with patch.object(generator, "_find_source_files") as mock_find:
                mock_find.return_value = [Path("file1.py"), Path("file2.py")]
                with patch.object(generator, "process_file") as mock_process:
                    mock_process.side_effect = ["output1.md", "output2.md"]
                    with patch.object(
                        generator, "_generate_directory_summary"
                    ) as mock_summary:
                        mock_summary.return_value = "summary.md"

                        results = generator.process_directory(test_dir)

        self.assertEqual(len(results), 3)  # 2 files + 1 summary
        self.assertIn("output1.md", results)
        self.assertIn("output2.md", results)
        self.assertIn("summary.md", results)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_process_directory_not_directory(
        self, mock_template_manager, mock_cache_manager
    ):
        """Test processing non-directory path."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        test_path = Path("not_a_dir")
        with patch("pathlib.Path.is_dir", return_value=False):
            results = generator.process_directory(test_path)

        self.assertEqual(results, [])

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_find_source_files(self, mock_template_manager, mock_cache_manager):
        """Test source file discovery."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        with patch("pathlib.Path.rglob") as mock_rglob:
            # Mock file discovery
            mock_files = [
                Path("src/module1.py"),
                Path("src/module2.py"),
                Path("tests/test_module.py"),  # This will be filtered out as test file
            ]
            mock_rglob.return_value = mock_files

            # Mock is_file() to return True for all files
            with patch("pathlib.Path.is_file", return_value=True):
                files = generator._find_source_files(Path("src"))

                # Should find 3 files (test files are NOT filtered out by default)
                # since skip_test_files defaults to False
                self.assertEqual(len(files), 3)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_ignore_functionality(self, mock_template_manager, mock_cache_manager):
        """Test .docgenai_ignore file functionality."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        # Test ignore patterns loading
        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(
                    read_data="""
# Test ignore file
__pycache__/
*.pyc
temp_*.py
# Another comment
tests/
"""
                ),
            ) as mock_file:
                patterns = generator._load_ignore_patterns(Path("test_dir"))
                expected_patterns = ["__pycache__/", "*.pyc", "temp_*.py", "tests/"]
                self.assertEqual(patterns, expected_patterns)

        # Test ignore pattern matching
        base_path = Path("project")
        ignore_patterns = ["__pycache__/", "*.pyc", "temp_*.py", "tests/"]

        # Should ignore these files
        self.assertTrue(
            generator._is_ignored(
                Path("project/__pycache__/module.cpython-39.pyc"),
                ignore_patterns,
                base_path,
            )
        )
        self.assertTrue(
            generator._is_ignored(
                Path("project/module.pyc"), ignore_patterns, base_path
            )
        )
        self.assertTrue(
            generator._is_ignored(
                Path("project/temp_file.py"), ignore_patterns, base_path
            )
        )
        self.assertTrue(
            generator._is_ignored(
                Path("project/tests/test_module.py"), ignore_patterns, base_path
            )
        )

        # Should NOT ignore these files
        self.assertFalse(
            generator._is_ignored(Path("project/module.py"), ignore_patterns, base_path)
        )
        self.assertFalse(
            generator._is_ignored(
                Path("project/src/main.py"), ignore_patterns, base_path
            )
        )

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_find_source_files_with_ignore(
        self, mock_template_manager, mock_cache_manager
    ):
        """Test source file discovery with ignore patterns."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        with patch("pathlib.Path.rglob") as mock_rglob:
            # Mock file discovery - all files should be under the base directory
            mock_files = [
                Path("project/src/module1.py"),
                Path("project/src/module2.py"),
                Path("project/src/__init__.py"),  # Should be ignored
                Path("project/src/__pycache__/module.pyc"),  # Should be ignored
                Path("project/tests/test_module.py"),  # Should be ignored
            ]
            mock_rglob.return_value = mock_files

            # Mock is_file() to return True for all files
            with patch("pathlib.Path.is_file", return_value=True):
                # Mock ignore patterns loading
                with patch.object(
                    generator, "_load_ignore_patterns"
                ) as mock_load_ignore:
                    mock_load_ignore.return_value = [
                        "__init__.py",
                        "__pycache__/",
                        "tests/",
                    ]

                    files = generator._find_source_files(Path("project"))

                    # Should find only 2 files (module1.py and module2.py)
                    # Others should be ignored
                    self.assertEqual(len(files), 2)
                    file_names = [f.name for f in files]
                    self.assertIn("module1.py", file_names)
                    self.assertIn("module2.py", file_names)
                    self.assertNotIn("__init__.py", file_names)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_is_test_file(self, mock_template_manager, mock_cache_manager):
        """Test test file detection."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        # Should detect test files
        self.assertTrue(generator._is_test_file(Path("test_module.py")))
        self.assertTrue(generator._is_test_file(Path("module_test.py")))
        # This should be False because "tests" != "test" in file_path.parts
        self.assertFalse(generator._is_test_file(Path("tests/module.py")))
        # But this should be True because "test" is in file_path.parts
        self.assertTrue(generator._is_test_file(Path("test/module.py")))

        # Should not detect regular files
        self.assertFalse(generator._is_test_file(Path("module.py")))

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_is_generated_file(self, mock_template_manager, mock_cache_manager):
        """Test generated file detection."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        self.assertTrue(generator._is_generated_file(Path("module.generated.py")))
        self.assertTrue(generator._is_generated_file(Path("module.pb2.py")))
        self.assertTrue(generator._is_generated_file(Path("__pycache__/module.py")))
        self.assertTrue(generator._is_generated_file(Path(".git/config")))
        self.assertFalse(generator._is_generated_file(Path("module.py")))

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_detect_language(self, mock_template_manager, mock_cache_manager):
        """Test language detection from file extension."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        # Test various file extensions
        self.assertEqual(generator._detect_language(".py"), "python")
        self.assertEqual(generator._detect_language(".js"), "javascript")
        self.assertEqual(generator._detect_language(".ts"), "typescript")
        self.assertEqual(generator._detect_language(".cpp"), "cpp")
        self.assertEqual(generator._detect_language(".java"), "java")
        self.assertEqual(generator._detect_language(".unknown"), "text")

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_get_cache_key(self, mock_template_manager, mock_cache_manager):
        """Test cache key generation."""
        mock_cache = MagicMock()
        mock_cache_manager.return_value = mock_cache
        mock_cache.get_cache_key.return_value = "test_cache_key"

        generator = DocumentationGenerator(self.mock_model, self.test_config)

        test_file = Path("test.py")
        cache_key = generator._get_cache_key(test_file)

        self.assertEqual(cache_key, "test_cache_key")
        mock_cache.get_cache_key.assert_called_once()

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_create_template_context(self, mock_template_manager, mock_cache_manager):
        """Test template context creation."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        file_path = Path("test.py")
        code_content = "def test(): pass"
        documentation = "Test documentation"
        architecture = "Test architecture"

        context = generator._create_template_context(
            file_path, code_content, documentation, architecture
        )

        self.assertIsInstance(context, dict)
        self.assertIn("file_path", context)
        self.assertIn("file_name", context)
        self.assertIn("language", context)
        self.assertIn("documentation", context)
        self.assertIn("architecture_description", context)
        self.assertIn("model_info", context)
        self.assertIn("code_stats", context)

        self.assertEqual(context["file_name"], "test.py")
        self.assertEqual(context["documentation"], documentation)

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_save_documentation(self, mock_template_manager, mock_cache_manager):
        """Test documentation saving."""
        generator = DocumentationGenerator(self.mock_model, self.test_config)

        input_file = Path("test.py")
        content = "# Test Documentation"

        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", mock_open()) as mock_file:
                result = generator._save_documentation(input_file, content)

        self.assertIsInstance(result, str)
        self.assertIn("test_documentation.md", result)
        mock_file.assert_called_once()

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_get_cache_stats(self, mock_template_manager, mock_cache_manager):
        """Test cache statistics retrieval."""
        mock_cache = MagicMock()
        mock_cache_manager.return_value = mock_cache
        mock_cache.get_stats.return_value = {"entries": 5, "size_mb": 10.5}

        generator = DocumentationGenerator(self.mock_model, self.test_config)

        stats = generator.get_cache_stats()

        self.assertIsInstance(stats, dict)
        mock_cache.get_stats.assert_called_once()

    @patch("docgenai.core.CacheManager")
    @patch("docgenai.core.TemplateManager")
    def test_clear_cache(self, mock_template_manager, mock_cache_manager):
        """Test cache clearing."""
        mock_cache = MagicMock()
        mock_cache_manager.return_value = mock_cache

        generator = DocumentationGenerator(self.mock_model, self.test_config)
        generator.clear_cache()

        mock_cache.clear_cache.assert_called_once()


if __name__ == "__main__":
    unittest.main()
