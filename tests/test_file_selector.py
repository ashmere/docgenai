"""
Test file selection functionality.

These tests don't require model downloads or external dependencies.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Import the file selector module
sys.path.insert(0, "src")
from docgenai.file_selector import FileSelector  # noqa: E402


class TestFileSelector:
    """Test file selection functionality."""

    @pytest.mark.unit
    def test_file_selector_creation(self):
        """Test that FileSelector can be created with default config."""
        config = {
            "file_selection": {
                "max_files": 50,
                "max_file_size": 10000,
                "include_patterns": ["*.py"],
                "exclude_patterns": ["*/__pycache__/*"],
            }
        }

        selector = FileSelector(config)
        assert selector is not None

    @pytest.mark.unit
    def test_pattern_matching(self):
        """Test that file patterns work correctly."""
        config = {
            "file_selection": {
                "max_files": 50,
                "max_file_size": 10000,
                "include_patterns": ["*.py", "*.js"],
                "exclude_patterns": ["test_*", "*/__pycache__/*"],
            }
        }

        selector = FileSelector(config)

        # Test with temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "main.py").touch()
            (temp_path / "script.js").touch()
            (temp_path / "test_file.py").touch()
            (temp_path / "README.md").touch()

            # Create __pycache__ directory
            pycache_dir = temp_path / "__pycache__"
            pycache_dir.mkdir()
            (pycache_dir / "cached.pyc").touch()

            files = selector.select_important_files(temp_path)
            file_names = [f.name for f in files]

            # Should include Python and JS files
            assert "main.py" in file_names
            assert "script.js" in file_names

            # Should exclude test files and cache files
            assert "test_file.py" not in file_names
            assert "cached.pyc" not in file_names

            # Should exclude non-matching extensions
            assert "README.md" not in file_names

    @pytest.mark.unit
    def test_max_files_limit(self):
        """Test that max_files limit is respected."""
        config = {
            "file_selection": {
                "max_files": 2,
                "max_file_size": 10000,
                "include_patterns": ["*.py"],
                "exclude_patterns": [],
            }
        }

        selector = FileSelector(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create more files than the limit
            for i in range(5):
                (temp_path / f"file_{i}.py").touch()

            files = selector.select_important_files(temp_path)

            # Should respect max_files limit
            assert len(files) <= 2

    @pytest.mark.unit
    def test_empty_directory(self):
        """Test behavior with empty directory."""
        config = {
            "file_selection": {
                "max_files": 50,
                "max_file_size": 10000,
                "include_patterns": ["*.py"],
                "exclude_patterns": [],
            }
        }

        selector = FileSelector(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            files = selector.select_important_files(temp_path)

            # Should return empty list for empty directory
            assert len(files) == 0

    @pytest.mark.unit
    def test_nonexistent_directory(self):
        """Test behavior with nonexistent directory."""
        config = {
            "file_selection": {
                "max_files": 50,
                "max_file_size": 10000,
                "include_patterns": ["*.py"],
                "exclude_patterns": [],
            }
        }

        selector = FileSelector(config)
        nonexistent_path = Path("/nonexistent/directory")

        # Should handle nonexistent directory gracefully
        files = selector.select_important_files(nonexistent_path)
        assert len(files) == 0
