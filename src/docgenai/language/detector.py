"""
Language detection system for universal codebase analysis.

Supports auto-detection with configurable override options for performance.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Universal language detection with configuration override support.

    Provides fast file extension-based detection with content-based
    fallback for ambiguous cases.
    """

    # Core language mappings for priority languages
    EXTENSION_MAP = {
        # Python
        ".py": "python",
        ".pyx": "python",
        ".pyi": "python",
        # TypeScript/JavaScript
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        # Go
        ".go": "go",
        # C++
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c++": "cpp",
        ".hpp": "cpp",
        ".hh": "cpp",
        ".hxx": "cpp",
        ".h++": "cpp",
        ".c": "c",
        ".h": "c",
        # DevOps/Infrastructure
        ".tf": "terraform",
        ".tfvars": "terraform",
        ".hcl": "terraform",
        ".yaml": "yaml",
        ".yml": "yaml",
        # Other supported languages
        ".java": "java",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
        ".sh": "shell",
        ".bash": "shell",
        ".zsh": "shell",
        ".fish": "shell",
        ".ps1": "powershell",
        ".sql": "sql",
        ".json": "json",
        ".xml": "xml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".conf": "ini",
        ".properties": "properties",
        ".dockerfile": "dockerfile",
        ".md": "markdown",
        ".rst": "rst",
        ".txt": "text",
    }

    # Special file name patterns
    FILENAME_PATTERNS = {
        "dockerfile": "dockerfile",
        "docker-compose": "yaml",
        "makefile": "makefile",
        "rakefile": "ruby",
        "gemfile": "ruby",
        "podfile": "ruby",
        "vagrantfile": "ruby",
        "requirements.txt": "text",
        "package.json": "json",
        "tsconfig.json": "json",
        "webpack.config.js": "javascript",
        "babel.config.js": "javascript",
        "jest.config.js": "javascript",
        "rollup.config.js": "javascript",
        "vite.config.ts": "typescript",
        "next.config.js": "javascript",
        "nuxt.config.js": "javascript",
        "vue.config.js": "javascript",
        "angular.json": "json",
        "cargo.toml": "toml",
        "pyproject.toml": "toml",
        "setup.py": "python",
        "setup.cfg": "ini",
        "tox.ini": "ini",
        "pytest.ini": "ini",
        "mypy.ini": "ini",
        "flake8.cfg": "ini",
        ".pylintrc": "ini",
        ".gitignore": "text",
        ".gitattributes": "text",
        ".editorconfig": "ini",
        ".env": "shell",
        ".env.example": "shell",
        ".env.local": "shell",
        ".env.production": "shell",
        ".env.development": "shell",
    }

    # Content-based detection patterns for ambiguous files
    CONTENT_PATTERNS = {
        "python": [
            r"^\s*import\s+\w+",
            r"^\s*from\s+\w+\s+import",
            r"^\s*def\s+\w+\s*\(",
            r"^\s*class\s+\w+\s*[:\(]",
            r"^\s*if\s+__name__\s*==\s*['\"]__main__['\"]",
        ],
        "javascript": [
            r"^\s*const\s+\w+\s*=",
            r"^\s*let\s+\w+\s*=",
            r"^\s*var\s+\w+\s*=",
            r"^\s*function\s+\w+\s*\(",
            r"^\s*export\s+(default\s+)?",
            r"^\s*import\s+.*\s+from\s+['\"]",
            r"require\s*\(['\"]",
        ],
        "typescript": [
            r"^\s*interface\s+\w+\s*{",
            r"^\s*type\s+\w+\s*=",
            r"^\s*enum\s+\w+\s*{",
            r":\s*\w+(\[\])?(\s*\|\s*\w+)*\s*[=;,)]",
            r"^\s*export\s+interface\s+",
            r"^\s*export\s+type\s+",
            r"^\s*import\s+type\s+",
        ],
        "go": [
            r"^\s*package\s+\w+",
            r"^\s*import\s+\(",
            r"^\s*func\s+\w*\s*\(",
            r"^\s*type\s+\w+\s+(struct|interface)",
            r"^\s*var\s+\w+\s+\w+",
            r"^\s*const\s+\w+\s*=",
        ],
        "cpp": [
            r"^\s*#include\s*[<\"]",
            r"^\s*#define\s+\w+",
            r"^\s*namespace\s+\w+",
            r"^\s*class\s+\w+\s*[:{]",
            r"^\s*struct\s+\w+\s*[:{]",
            r"^\s*template\s*<",
            r"^\s*using\s+namespace\s+",
        ],
        "terraform": [
            r"^\s*resource\s+['\"][^'\"]+['\"]",
            r"^\s*variable\s+['\"][^'\"]+['\"]",
            r"^\s*output\s+['\"][^'\"]+['\"]",
            r"^\s*module\s+['\"][^'\"]+['\"]",
            r"^\s*provider\s+['\"][^'\"]+['\"]",
            r"^\s*terraform\s*{",
        ],
    }

    def __init__(self, language_override: Optional[str] = None):
        """
        Initialize language detector.

        Args:
            language_override: Optional language to use instead of detection
        """
        self.language_override = language_override
        self.detection_cache: Dict[str, str] = {}

        if language_override:
            logger.info(f"🔧 Language detection override: {language_override}")

    def detect_language(self, file_path: Path) -> str:
        """
        Detect the programming language of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Detected language identifier
        """
        if self.language_override:
            return self.language_override

        file_str = str(file_path)
        if file_str in self.detection_cache:
            return self.detection_cache[file_str]

        # Try extension-based detection first
        language = self._detect_by_extension(file_path)

        # Try filename pattern detection
        if language == "text":
            language = self._detect_by_filename(file_path)

        # For ambiguous cases, use content-based detection
        if language in ["text", "c"] and file_path.exists():
            content_language = self._detect_by_content(file_path)
            if content_language:
                language = content_language

        # Cache result
        self.detection_cache[file_str] = language

        return language

    def _detect_by_extension(self, file_path: Path) -> str:
        """Detect language by file extension."""
        extension = file_path.suffix.lower()
        return self.EXTENSION_MAP.get(extension, "text")

    def _detect_by_filename(self, file_path: Path) -> str:
        """Detect language by filename patterns."""
        filename = file_path.name.lower()

        # Check exact matches first
        if filename in self.FILENAME_PATTERNS:
            return self.FILENAME_PATTERNS[filename]

        # Check partial matches
        for pattern, language in self.FILENAME_PATTERNS.items():
            if pattern in filename:
                return language

        return "text"

    def _detect_by_content(self, file_path: Path, max_lines: int = 50) -> Optional[str]:
        """
        Detect language by analyzing file content.

        Args:
            file_path: Path to file to analyze
            max_lines: Maximum lines to read for detection

        Returns:
            Detected language or None if uncertain
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)

                content = "".join(lines)

            # Score each language based on pattern matches
            scores = {}
            for language, patterns in self.CONTENT_PATTERNS.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.MULTILINE))
                    score += matches

                if score > 0:
                    scores[language] = score

            # Return language with highest score
            if scores:
                return max(scores, key=scores.get)

            return None

        except (IOError, UnicodeDecodeError):
            return None

    def get_supported_languages(self) -> Set[str]:
        """Get set of all supported languages."""
        languages = set(self.EXTENSION_MAP.values())
        languages.update(self.FILENAME_PATTERNS.values())
        return languages

    def is_source_file(self, file_path: Path) -> bool:
        """
        Check if a file is a source code file.

        Args:
            file_path: Path to check

        Returns:
            True if file appears to be source code
        """
        language = self.detect_language(file_path)

        # Exclude documentation and configuration files from source analysis
        non_source_languages = {
            "text",
            "markdown",
            "rst",
            "json",
            "xml",
            "ini",
            "properties",
            "yaml",
            "toml",
        }

        return language not in non_source_languages

    def get_language_group(self, language: str) -> str:
        """
        Get the language group for semantic grouping.

        Args:
            language: Language identifier

        Returns:
            Language group (e.g., 'web_frontend', 'systems', 'devops')
        """
        groups = {
            "web_frontend": ["javascript", "typescript", "jsx"],
            "web_backend": ["python", "java", "go", "csharp", "php", "ruby"],
            "systems": ["cpp", "c", "rust", "go"],
            "mobile": ["swift", "kotlin", "java"],
            "devops": ["terraform", "yaml", "shell", "dockerfile"],
            "data": ["python", "r", "sql", "scala"],
            "config": ["json", "yaml", "toml", "ini", "xml"],
            "documentation": ["markdown", "rst", "text"],
        }

        for group, languages in groups.items():
            if language in languages:
                return group

        return "other"

    def clear_cache(self):
        """Clear the detection cache."""
        self.detection_cache.clear()
        logger.debug("🧹 Language detection cache cleared")
