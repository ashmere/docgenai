"""
Multi-file analyzer for DocGenAI.

Analyzes multiple related code files together to generate better documentation
by understanding cross-file relationships and dependencies.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class MultiFileAnalyzer:
    """
    Analyzes multiple code files together for comprehensive documentation.

    Works with current DeepSeek-V2-Lite models (32k context window).
    """

    def __init__(self, config: Dict):
        """Initialize the multi-file analyzer."""
        self.config = config
        self.model_config = config.get("model", {})

        # Token limits for current DeepSeek-V2-Lite (32k context)
        self.max_context_tokens = 30000  # Leave buffer for output
        self.max_output_tokens = self.model_config.get("max_tokens", 4000)
        self.chars_per_token = 3.5  # Approximate for code

        # File grouping limits
        self.max_files_per_group = self.model_config.get("max_files_per_group", 8)
        self.max_file_size_chars = 15000  # Increased for real-world files

        logger.info("🔗 Multi-file analyzer initialized")
        logger.info(f"📊 Max context: {self.max_context_tokens} tokens")
        logger.info(f"📁 Max files per group: {self.max_files_per_group}")
        logger.info(f"📄 Max file size: {self.max_file_size_chars} chars")

    def group_files_for_analysis(self, file_paths: List[Path]) -> List[List[Path]]:
        """
        Group files for multi-file analysis.

        Based on relationships and token limits.

        Args:
            file_paths: List of source code files to group

        Returns:
            List of file groups, each suitable for analysis together
        """
        logger.info(f"📂 Grouping {len(file_paths)} files for multi-file analysis")

        # Filter out files that are too large
        suitable_files = []
        for file_path in file_paths:
            try:
                file_size = file_path.stat().st_size
                if file_size > self.max_file_size_chars:
                    logger.warning(
                        f"⚠️  Skipping large file: {file_path} " f"({file_size} chars)"
                    )
                    continue
                suitable_files.append(file_path)
            except Exception as e:
                logger.warning(f"⚠️  Error checking file size {file_path}: {e}")
                continue

        logger.info(
            f"📋 {len(suitable_files)} files suitable for " "multi-file analysis"
        )

        # Group files by directory (primary strategy)
        groups = self._group_by_directory(suitable_files)

        # Refine groups to fit token limits
        final_groups = []
        for group in groups:
            final_groups.extend(self._split_group_by_token_limit(group))

        logger.info(f"🎯 Created {len(final_groups)} file groups")
        for i, group in enumerate(final_groups):
            logger.info(f"  Group {i+1}: {len(group)} files")

        return final_groups

    def _group_by_directory(self, file_paths: List[Path]) -> List[List[Path]]:
        """Group files by their directory structure."""
        directory_groups = {}

        for file_path in file_paths:
            # Use parent directory as grouping key
            dir_key = str(file_path.parent)
            if dir_key not in directory_groups:
                directory_groups[dir_key] = []
            directory_groups[dir_key].append(file_path)

        # Convert to list of groups
        groups = list(directory_groups.values())

        # Sort groups by size (larger groups first for better splitting)
        groups.sort(key=len, reverse=True)

        return groups

    def _split_group_by_token_limit(self, file_group: List[Path]) -> List[List[Path]]:
        """Split a file group to fit within token limits."""
        if len(file_group) <= self.max_files_per_group:
            # Check if group fits in token limit
            total_chars = self._estimate_group_size(file_group)
            estimated_tokens = total_chars / self.chars_per_token

            if estimated_tokens <= self.max_context_tokens:
                return [file_group]

        # Split into smaller groups
        subgroups = []
        current_group = []
        current_size = 0

        for file_path in file_group:
            file_size = self._estimate_file_size(file_path)
            file_tokens = file_size / self.chars_per_token

            # Check if adding this file would exceed limits
            if (
                len(current_group) >= self.max_files_per_group
                or current_size + file_tokens > self.max_context_tokens
            ):

                if current_group:
                    subgroups.append(current_group)
                current_group = [file_path]
                current_size = file_tokens
            else:
                current_group.append(file_path)
                current_size += file_tokens

        # Add final group
        if current_group:
            subgroups.append(current_group)

        return subgroups

    def _estimate_file_size(self, file_path: Path) -> int:
        """Estimate file size in characters."""
        try:
            return file_path.stat().st_size
        except Exception:
            return 1000  # Default estimate

    def _estimate_group_size(self, file_group: List[Path]) -> int:
        """Estimate total size of a file group in characters."""
        return sum(self._estimate_file_size(f) for f in file_group)

    def prepare_multi_file_context(self, file_group: List[Path]) -> Dict[str, str]:
        """
        Prepare context for multi-file analysis.

        Args:
            file_group: List of files to analyze together

        Returns:
            Dictionary with prepared context for the AI model
        """
        logger.info(f"📝 Preparing context for {len(file_group)} files")

        files_content = []
        file_summaries = []

        for file_path in file_group:
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Create file entry
                relative_path = self._get_relative_path(file_path)
                language = self._detect_language(file_path)
                file_entry = (
                    f"## File: {relative_path}\n\n" f"```{language}\n{content}\n```\n"
                )
                files_content.append(file_entry)

                # Create summary entry
                file_info = self._analyze_file_structure(content, file_path)
                file_summaries.append(f"- **{relative_path}**: {file_info}")

            except Exception as e:
                logger.warning(f"⚠️  Error reading file {file_path}: {e}")
                continue

        # Combine all content
        combined_content = "\n".join(files_content)
        files_summary = "\n".join(file_summaries)

        # Estimate token usage
        estimated_tokens = len(combined_content) / self.chars_per_token
        logger.info(f"📊 Estimated input tokens: {estimated_tokens:.0f}")

        return {
            "files_content": combined_content,
            "files_summary": files_summary,
            "file_count": len(file_group),
            "file_names": [str(f.name) for f in file_group],
            "estimated_tokens": estimated_tokens,
        }

    def _get_relative_path(self, file_path: Path) -> str:
        """Get relative path for display."""
        try:
            return str(file_path.relative_to(Path.cwd()))
        except ValueError:
            return str(file_path)

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension = file_path.suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
        }
        return language_map.get(extension, "text")

    def _analyze_file_structure(self, content: str, file_path: Path) -> str:
        """Analyze file structure to create a brief summary."""
        lines = content.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]

        # Count different types of definitions
        classes = len(re.findall(r"^\s*class\s+\w+", content, re.MULTILINE))
        functions = len(
            re.findall(r"^\s*def\s+\w+|^\s*function\s+\w+", content, re.MULTILINE)
        )
        imports = len(
            re.findall(r"^\s*import\s+|^\s*from\s+\w+\s+import", content, re.MULTILINE)
        )

        # Create summary
        parts = []
        if classes > 0:
            parts.append(f"{classes} class{'es' if classes > 1 else ''}")
        if functions > 0:
            parts.append(f"{functions} function{'s' if functions > 1 else ''}")
        if imports > 0:
            parts.append(f"{imports} import{'s' if imports > 1 else ''}")

        if parts:
            structure = ", ".join(parts)
        else:
            structure = f"{len(non_empty_lines)} lines of code"

        return structure

    def should_use_multi_file_analysis(self, file_paths: List[Path]) -> bool:
        """
        Determine if multi-file analysis would be beneficial.

        Args:
            file_paths: List of files to potentially analyze together

        Returns:
            True if multi-file analysis is recommended
        """
        if len(file_paths) < 2:
            return False

        # Check if files are related (same directory, similar names, etc.)
        if len(file_paths) <= 5:
            # For small groups, multi-file analysis is usually beneficial
            return True

        # For larger groups, check if they're in related directories
        directories = set(f.parent for f in file_paths)
        if len(directories) <= 3:
            # Files are in few directories, likely related
            return True

        return False

    def analyze_codebase_structure(self, root_path: Path) -> Dict[str, any]:
        """
        Analyze the structure of an entire codebase.

        Args:
            root_path: Root directory of the codebase

        Returns:
            Dictionary with codebase structure analysis
        """
        logger.info(f"🏗️  Analyzing codebase structure: {root_path}")

        # Find all source files
        source_files = self._find_source_files(root_path)

        # Group files for analysis
        groups = self.group_files_for_analysis(source_files)

        # Analyze structure
        structure = {
            "root_path": str(root_path),
            "total_files": len(source_files),
            "suitable_files": sum(len(group) for group in groups),
            "groups": len(groups),
            "group_details": [],
            "large_files": [],
            "estimated_total_tokens": 0,
            "requires_synthesis": len(groups) > 1,
        }

        # Analyze each group
        for i, group in enumerate(groups):
            context = self.prepare_multi_file_context(group)
            group_info = {
                "group_id": i + 1,
                "files": [f.name for f in group],
                "file_count": len(group),
                "estimated_tokens": context["estimated_tokens"],
                "primary_directory": str(group[0].parent) if group else "",
            }
            structure["group_details"].append(group_info)
            structure["estimated_total_tokens"] += context["estimated_tokens"]

        # Find large files that were skipped
        for file_path in source_files:
            file_size = self._estimate_file_size(file_path)
            if file_size > self.max_file_size_chars:
                structure["large_files"].append(
                    {
                        "file": str(file_path),
                        "size": file_size,
                        "reason": "Exceeds size limit",
                    }
                )

        logger.info(f"📊 Codebase analysis complete:")
        logger.info(f"  - {structure['total_files']} total files")
        logger.info(f"  - {structure['groups']} analysis groups")
        logger.info(f"  - {structure['estimated_total_tokens']:.0f} total tokens")
        logger.info(f"  - Synthesis needed: {structure['requires_synthesis']}")

        return structure

    def _find_source_files(self, root_path: Path) -> List[Path]:
        """Find all source code files in the codebase."""
        source_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".cc",
            ".cxx",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".cs",
            ".swift",
            ".kt",
            ".scala",
            ".r",
        }

        source_files = []

        # Common directories to skip
        skip_dirs = {
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            "vendor",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            ".env",
            "venv",
            ".venv",
            "env",
        }

        for file_path in root_path.rglob("*"):
            # Skip directories and non-files
            if not file_path.is_file():
                continue

            # Skip files in excluded directories
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            # Check if it's a source file
            if file_path.suffix.lower() in source_extensions:
                source_files.append(file_path)

        logger.info(f"📁 Found {len(source_files)} source files")
        return source_files

    def create_group_summaries(self, groups: List[List[Path]]) -> List[Dict]:
        """
        Create summaries for each file group for cross-group analysis.

        Args:
            groups: List of file groups

        Returns:
            List of group summaries
        """
        summaries = []

        for i, group in enumerate(groups):
            context = self.prepare_multi_file_context(group)

            # Create a concise summary of the group
            summary = {
                "group_id": i + 1,
                "primary_directory": str(group[0].parent) if group else "",
                "files": context["file_names"],
                "file_count": context["file_count"],
                "summary": context["files_summary"],
                "estimated_tokens": context["estimated_tokens"],
                "key_components": self._extract_key_components(group),
            }

            summaries.append(summary)

        return summaries

    def _extract_key_components(self, file_group: List[Path]) -> List[str]:
        """Extract key components (classes, functions) from a file group."""
        components = []

        for file_path in file_group:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract class names
                import re

                classes = re.findall(r"^\s*class\s+(\w+)", content, re.MULTILINE)
                functions = re.findall(
                    r"^\s*(?:def|function)\s+(\w+)", content, re.MULTILINE
                )

                # Add to components with file context
                for cls in classes:
                    components.append(f"{file_path.name}::{cls}")

                # Add main functions (not starting with _)
                for func in functions:
                    if not func.startswith("_"):
                        components.append(f"{file_path.name}::{func}")

            except Exception:
                continue

        return components[:10]  # Limit to most important components

    def estimate_synthesis_complexity(self, codebase_structure: Dict) -> str:
        """
        Estimate the complexity of synthesis needed for the codebase.

        Args:
            codebase_structure: Output from analyze_codebase_structure

        Returns:
            Complexity level: "simple", "moderate", "complex"
        """
        groups = codebase_structure["groups"]
        total_files = codebase_structure["total_files"]
        total_tokens = codebase_structure["estimated_total_tokens"]

        if groups <= 2 and total_files <= 10:
            return "simple"
        elif groups <= 5 and total_files <= 25 and total_tokens <= 50000:
            return "moderate"
        else:
            return "complex"
