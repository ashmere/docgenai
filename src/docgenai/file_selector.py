"""
Smart File Selector for DocGenAI

This module implements intelligent heuristics to identify the most important
files in a codebase for documentation generation. It focuses on entry points,
configuration, APIs, core business logic, and existing documentation.
"""

import fnmatch
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class SmartFileSelector:
    """Select the most important files for documentation using intelligent
    heuristics."""

    def __init__(self, config: Dict):
        """Initialize the file selector with configuration."""
        self.config = config
        self.file_config = config.get("file_selection", {})
        self.max_files = self.file_config.get("max_files", 50)
        self.max_file_size = self.file_config.get("max_file_size", 10000)
        self.include_patterns = self.file_config.get(
            "include_patterns",
            [
                "*.py",
                "*.js",
                "*.ts",
                "*.jsx",
                "*.tsx",
                "*.go",
                "*.java",
                "*.cpp",
                "*.c",
                "*.h",
                "*.hpp",
                "*.rs",
                "*.rb",
                "*.php",
            ],
        )
        self.exclude_patterns = self.file_config.get(
            "exclude_patterns",
            [
                "*/node_modules/*",
                "*/__pycache__/*",
                "*/vendor/*",
                "*/build/*",
                "*/dist/*",
                "*/target/*",
                "*/.git/*",
                "*/venv/*",
                "*/env/*",
            ],
        )

        # File priority patterns
        self.entry_point_patterns = [
            "main.py",
            "app.py",
            "server.py",
            "__main__.py",
            "manage.py",
            "index.js",
            "server.js",
            "app.js",
            "main.js",
            "index.ts",
            "main.go",
            "cmd/*/main.go",
            "src/main/*",
            "Main.java",
            "main.cpp",
            "main.c",
            "main.rs",
            "index.php",
        ]

        self.config_patterns = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "go.mod",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            "composer.json",
            "*.config.*",
            "docker-compose.*",
            "Dockerfile",
            "Makefile",
            ".env*",
            "config.*",
            "settings.*",
        ]

        self.api_patterns = [
            "**/routes/**",
            "**/controllers/**",
            "**/handlers/**",
            "**/api/**",
            "**/endpoints/**",
            "**/services/**",
            "**/*_controller.*",
            "**/*_handler.*",
            "**/*_service.*",
            "**/*_router.*",
            "**/*_api.*",
            "**/views/**",
        ]

        self.doc_patterns = [
            "README*",
            "readme*",
            "CHANGELOG*",
            "changelog*",
            "docs/**",
            "documentation/**",
            "*.md",
            "*.rst",
            "*.txt",
        ]

    def select_important_files(self, codebase_path: Path) -> List[Path]:
        """
        Select the most important files for documentation.

        Args:
            codebase_path: Root path of the codebase

        Returns:
            List of selected file paths, prioritized and limited
        """
        logger.info(f"🔍 Analyzing codebase at {codebase_path}")

        # Handle single file case
        if codebase_path.is_file():
            root_path = codebase_path.parent
            if self._should_include_file(codebase_path, root_path):
                logger.info(f"📄 Single file selected: {codebase_path.name}")
                return [codebase_path]
            else:
                logger.warning(
                    f"⚠️ Single file does not match include patterns: {codebase_path.name}"
                )
                return []

        # Find all source files first
        all_files = self._find_all_source_files(codebase_path)
        logger.info(f"📁 Found {len(all_files)} source files")

        # Categorize files by importance
        categorized_files = self._categorize_files(all_files, codebase_path)

        # Prioritize and select files
        selected_files = self._prioritize_and_limit(categorized_files)

        logger.info(f"✅ Selected {len(selected_files)} important files")
        return selected_files

    def _find_all_source_files(self, codebase_path: Path) -> List[Path]:
        """Find all source files matching include patterns."""
        all_files = []

        for pattern in self.include_patterns:
            # Use rglob for recursive search
            files = list(codebase_path.rglob(pattern))
            all_files.extend(files)

        # Remove duplicates and filter out excluded files
        unique_files = list(set(all_files))
        filtered_files = []

        for file_path in unique_files:
            if self._should_include_file(file_path, codebase_path):
                filtered_files.append(file_path)

        return filtered_files

    def _should_include_file(self, file_path: Path, root_path: Path) -> bool:
        """Check if a file should be included based on exclude patterns."""
        try:
            # Check if file is readable
            if not file_path.is_file() or not file_path.exists():
                return False

            # Get relative path for pattern matching
            rel_path = file_path.relative_to(root_path)
            rel_path_str = str(rel_path)

            # Check exclude patterns
            for pattern in self.exclude_patterns:
                if fnmatch.fnmatch(rel_path_str, pattern):
                    return False

            # Check file size (skip very large files)
            try:
                max_size = self.max_file_size * 10  # 10x threshold
                if file_path.stat().st_size > max_size:
                    logger.debug(f"Skipping large file: {rel_path_str}")
                    return False
            except (OSError, PermissionError):
                return False

            return True

        except (ValueError, OSError, PermissionError):
            return False

    def _categorize_files(
        self, files: List[Path], root_path: Path
    ) -> Dict[str, List[Tuple[Path, int]]]:
        """Categorize files by type and assign priority scores."""
        categories = {
            "entry_points": [],
            "config_files": [],
            "api_files": [],
            "core_files": [],
            "doc_files": [],
        }

        for file_path in files:
            rel_path = str(file_path.relative_to(root_path))
            file_name = file_path.name

            # Calculate base priority score
            priority_score = self._calculate_priority_score(file_path, root_path)

            # Categorize file
            if self._matches_patterns(rel_path, file_name, self.entry_point_patterns):
                categories["entry_points"].append((file_path, priority_score + 100))
            elif self._matches_patterns(rel_path, file_name, self.config_patterns):
                categories["config_files"].append((file_path, priority_score + 80))
            elif self._matches_patterns(rel_path, file_name, self.api_patterns):
                categories["api_files"].append((file_path, priority_score + 60))
            elif self._matches_patterns(rel_path, file_name, self.doc_patterns):
                categories["doc_files"].append((file_path, priority_score + 40))
            else:
                categories["core_files"].append((file_path, priority_score))

        # Sort each category by priority score
        for category in categories.values():
            category.sort(key=lambda x: x[1], reverse=True)

        return categories

    def _matches_patterns(
        self, rel_path: str, file_name: str, patterns: List[str]
    ) -> bool:
        """Check if a file matches any of the given patterns."""
        for pattern in patterns:
            # Check exact filename match
            if fnmatch.fnmatch(file_name, pattern):
                return True
            # Check relative path match
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Check if pattern is in the path
            if pattern.replace("**/", "").replace("/**", "") in rel_path:
                return True
        return False

    def _calculate_priority_score(self, file_path: Path, root_path: Path) -> int:
        """Calculate priority score based on file characteristics."""
        score = 0

        try:
            # File size factor (medium-sized files are often more important)
            file_size = file_path.stat().st_size
            if 1000 <= file_size <= 10000:  # Sweet spot for important files
                score += 20
            elif file_size <= 1000:
                score += 5
            elif file_size <= 50000:
                score += 10

            # Directory depth (files closer to root are often more important)
            rel_path = file_path.relative_to(root_path)
            depth = len(rel_path.parts) - 1
            score += max(0, 20 - depth * 3)  # Decrease score with depth

            # File extension priority
            ext = file_path.suffix.lower()
            ext_priorities = {
                ".py": 15,
                ".js": 15,
                ".ts": 15,
                ".go": 15,
                ".java": 15,
                ".cpp": 10,
                ".c": 10,
                ".h": 10,
                ".rs": 10,
                ".rb": 10,
                ".jsx": 12,
                ".tsx": 12,
                ".php": 8,
                ".cs": 8,
            }
            score += ext_priorities.get(ext, 0)

            # Special filename indicators
            file_name_lower = file_path.name.lower()
            if any(
                keyword in file_name_lower
                for keyword in ["main", "app", "server", "index"]
            ):
                score += 25
            if any(
                keyword in file_name_lower
                for keyword in ["config", "settings", "setup"]
            ):
                score += 20
            if any(
                keyword in file_name_lower
                for keyword in ["api", "route", "controller", "service"]
            ):
                score += 15
            if any(keyword in file_name_lower for keyword in ["test", "spec", "mock"]):
                score -= 10  # Lower priority for test files

        except (OSError, PermissionError):
            pass

        return score

    def _prioritize_and_limit(
        self, categorized_files: Dict[str, List[Tuple[Path, int]]]
    ) -> List[Path]:
        """Prioritize files across categories and limit to max_files."""
        selected_files = []

        # Define how many files to take from each category (proportional)
        category_limits = {
            "entry_points": min(5, len(categorized_files["entry_points"])),
            "config_files": min(8, len(categorized_files["config_files"])),
            "api_files": min(15, len(categorized_files["api_files"])),
            "doc_files": min(5, len(categorized_files["doc_files"])),
            "core_files": min(25, len(categorized_files["core_files"])),
        }

        # Select files from each category
        for category, limit in category_limits.items():
            category_files = categorized_files[category][:limit]
            selected_files.extend([file_path for file_path, _ in category_files])

        # If we have fewer files than max_files, add more core files
        if len(selected_files) < self.max_files:
            remaining_slots = self.max_files - len(selected_files)
            additional_core = categorized_files["core_files"][
                category_limits["core_files"] :
            ]
            additional_files = [
                file_path for file_path, _ in additional_core[:remaining_slots]
            ]
            selected_files.extend(additional_files)

        # If we still have too many files, prioritize by overall score
        if len(selected_files) > self.max_files:
            # Recalculate scores for final selection
            all_files_with_scores = []
            for category, files in categorized_files.items():
                all_files_with_scores.extend(files)

            # Sort by score and take top files
            all_files_with_scores.sort(key=lambda x: x[1], reverse=True)
            selected_files = [
                file_path for file_path, _ in all_files_with_scores[: self.max_files]
            ]

        # Log selection summary
        self._log_selection_summary(categorized_files, selected_files)

        return selected_files

    def _log_selection_summary(
        self,
        categorized_files: Dict[str, List[Tuple[Path, int]]],
        selected_files: List[Path],
    ) -> None:
        """Log a summary of the file selection process."""
        logger.info("📊 File selection summary:")

        selected_set = set(selected_files)
        for category, files in categorized_files.items():
            category_selected = sum(
                1 for file_path, _ in files if file_path in selected_set
            )
            logger.info(f"  {category}: {category_selected}/{len(files)} selected")

        # Log some example selected files
        logger.info("📋 Example selected files:")
        for i, file_path in enumerate(selected_files[:10]):
            logger.info(f"  {i+1}. {file_path.name}")

        if len(selected_files) > 10:
            logger.info(f"  ... and {len(selected_files) - 10} more files")
