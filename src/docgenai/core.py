"""
Core documentation generation logic for DocGenAI.

This module handles the main workflow of analyzing code files/directories
and generating comprehensive documentation using DeepSeek-Coder models
with platform-aware optimization and comprehensive configuration support.
"""

import fnmatch
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache import CacheManager
from .config import (
    get_cache_config,
    get_generation_config,
    get_model_config,
    get_output_config,
    load_config,
)
from .models import AIModel, create_model
from .templates import TemplateManager

logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """
    Main class for generating documentation from code.

    Handles file processing, model interaction, template rendering,
    and output generation with comprehensive caching support and
    platform-aware model optimization.
    """

    def __init__(self, model: AIModel, config: Dict[str, Any]):
        """
        Initialize the documentation generator.

        Args:
            model: Initialized AI model instance
            config: Complete configuration dictionary
        """
        self.model = model
        self.config = config

        # Extract configuration sections
        self.cache_config = get_cache_config(config)
        self.output_config = get_output_config(config)
        self.generation_config = get_generation_config(config)
        self.model_config = get_model_config(config)

        # Initialize components
        self.cache_manager = CacheManager(self.cache_config)
        self.template_manager = TemplateManager(config.get("templates", {}))

        logger.info("🚀 DocumentationGenerator initialized")
        logger.info(f"📋 Model: {self.model.get_model_info()['model_path']}")
        logger.info(f"⚙️  Backend: {self.model.get_model_info()['backend']}")

    def process_file(self, file_path: Path) -> Optional[str]:
        """
        Process a single file and generate documentation.

        Args:
            file_path: Path to the source code file

        Returns:
            Path to generated documentation file, or None if failed
        """
        logger.info(f"📝 Processing file: {file_path}")
        start_time = time.time()

        try:
            # Validate input file
            if not file_path.exists():
                logger.error(f"❌ File not found: {file_path}")
                return None

            # Check file size limits
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            max_size_mb = self.generation_config.get("max_file_size_mb", 10)

            if file_size_mb > max_size_mb:
                logger.warning(
                    f"⚠️  File too large ({file_size_mb:.1f}MB > {max_size_mb}MB): "
                    f"{file_path}"
                )
                return None

            # Check cache first
            cache_key = self._get_cache_key(file_path)
            cached_result = self.cache_manager.get_cached_result(cache_key)

            if cached_result:
                logger.info("💾 Using cached result")
                return cached_result.get("output_file")

            # Read source code
            logger.info("📖 Reading source code...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code_content = f.read()
            except UnicodeDecodeError:
                logger.warning("⚠️  UTF-8 decode failed, trying with error handling...")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()

            logger.info(f"📊 Code length: {len(code_content)} characters")

            # Generate documentation
            logger.info("🔄 Generating documentation...")
            doc_start = time.time()
            documentation = self.model.generate_documentation(
                code_content, str(file_path)
            )
            doc_elapsed = time.time() - doc_start
            logger.info(f"✅ Documentation generated in {doc_elapsed:.2f} seconds")

            # Generate architecture description if requested
            architecture_description = ""
            if self.output_config.get("include_architecture", True):
                logger.info("🏗️  Generating architecture description...")
                arch_start = time.time()
                architecture_description = self.model.generate_architecture_description(
                    code_content,
                    str(file_path),
                    include_diagrams=self.output_config.get("include_diagrams", True),
                )
                arch_elapsed = time.time() - arch_start
                logger.info(
                    f"✅ Architecture description generated in "
                    f"{arch_elapsed:.2f} seconds"
                )

            # Prepare template context
            context = self._create_template_context(
                file_path, code_content, documentation, architecture_description
            )

            # Render template
            logger.info("📄 Rendering documentation template...")
            rendered_doc = self.template_manager.render_documentation(context)

            # Clean up formatting issues
            rendered_doc = clean_documentation_output(rendered_doc)

            # Save output
            output_path = self._save_documentation(file_path, rendered_doc)

            # Prepare result for caching
            result = {
                "input_file": str(file_path),
                "output_file": output_path,
                "documentation": documentation,
                "architecture_description": architecture_description,
                "context": context,
                "generation_time": time.time() - start_time,
                "cache_key": cache_key,
            }

            # Cache result
            self.cache_manager.cache_result(cache_key, result)

            total_elapsed = time.time() - start_time
            logger.info(f"🎉 File processing complete in {total_elapsed:.2f} seconds")
            logger.info(f"💾 Saved to: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {str(e)}")
            return None

    def process_directory(self, dir_path: Path) -> List[str]:
        """
        Process all files in a directory and generate documentation.

        Args:
            dir_path: Path to the source directory

        Returns:
            List of paths to generated documentation files
        """
        logger.info(f"📁 Processing directory: {dir_path}")
        start_time = time.time()

        if not dir_path.is_dir():
            logger.error(f"❌ Not a directory: {dir_path}")
            return []

        # Find source files
        source_files = self._find_source_files(dir_path)

        if not source_files:
            logger.warning(f"⚠️  No source files found in {dir_path}")
            return []

        logger.info(f"🔍 Found {len(source_files)} files to process")

        # Process files
        results = []
        successful = 0
        failed = 0

        for file_path in source_files:
            try:
                result = self.process_file(file_path)
                if result:
                    results.append(result)
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ Failed to process {file_path}: {str(e)}")
                failed += 1

        # Generate directory summary if enabled
        if self.output_config.get("create_subdirs", True) and results:
            summary_path = self._generate_directory_summary(dir_path, results)
            if summary_path:
                results.append(summary_path)

        total_elapsed = time.time() - start_time
        logger.info(f"🎉 Directory processing complete in {total_elapsed:.2f} seconds")
        logger.info(f"📊 Results: {successful} successful, {failed} failed")

        return results

    def _load_ignore_patterns(self, dir_path: Path) -> List[str]:
        """Load ignore patterns from .docgenai_ignore file."""
        ignore_file = dir_path / ".docgenai_ignore"
        patterns = []

        if ignore_file.exists():
            try:
                with open(ignore_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith("#"):
                            patterns.append(line)
                logger.info(
                    f"📋 Loaded {len(patterns)} ignore patterns from {ignore_file}"
                )
            except Exception as e:
                logger.warning(f"⚠️  Failed to read {ignore_file}: {e}")

        return patterns

    def _is_ignored(
        self, file_path: Path, ignore_patterns: List[str], base_path: Path
    ) -> bool:
        """Check if file should be ignored based on patterns."""
        if not ignore_patterns:
            return False

        # Get relative path for pattern matching
        try:
            rel_path = file_path.relative_to(base_path)
            rel_path_str = str(rel_path)
            rel_path_posix = rel_path_str.replace(os.sep, "/")

            for pattern in ignore_patterns:
                # Convert pattern to use forward slashes for consistency
                pattern_posix = pattern.replace("\\", "/")

                # Check various forms of the path
                if (
                    fnmatch.fnmatch(rel_path_posix, pattern_posix)
                    or fnmatch.fnmatch(rel_path_str, pattern)
                    or fnmatch.fnmatch(file_path.name, pattern)
                    or pattern_posix in rel_path_posix
                ):
                    return True

                # Check if any parent directory matches the pattern
                for parent in rel_path.parents:
                    parent_str = str(parent).replace(os.sep, "/")
                    if fnmatch.fnmatch(parent_str, pattern_posix):
                        return True

        except ValueError:
            # file_path is not relative to base_path
            pass

        return False

    def _find_source_files(self, dir_path: Path) -> List[Path]:
        """Find source files in directory based on configured patterns."""
        file_patterns = self.generation_config.get("file_patterns", ["*.py"])
        skip_test_files = self.generation_config.get("skip_test_files", False)
        skip_generated_files = self.generation_config.get("skip_generated_files", True)

        # Load ignore patterns from .docgenai_ignore file
        ignore_patterns = self._load_ignore_patterns(dir_path)

        source_files = []

        for pattern in file_patterns:
            files = list(dir_path.rglob(pattern))

            for file_path in files:
                # Skip if not a file
                if not file_path.is_file():
                    continue

                # Skip if file matches ignore patterns
                if self._is_ignored(file_path, ignore_patterns, dir_path):
                    logger.debug(f"🚫 Ignoring file: {file_path}")
                    continue

                # Skip test files if configured
                if skip_test_files and self._is_test_file(file_path):
                    continue

                # Skip generated files if configured
                if skip_generated_files and self._is_generated_file(file_path):
                    continue

                source_files.append(file_path)

        # Remove duplicates and sort
        source_files = sorted(set(source_files))

        return source_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file appears to be a test file."""
        name_lower = file_path.name.lower()
        return (
            name_lower.startswith("test_")
            or name_lower.endswith("_test.py")
            or "test" in file_path.parts
        )

    def _is_generated_file(self, file_path: Path) -> bool:
        """Check if file appears to be generated."""
        name_lower = file_path.name.lower()
        return (
            name_lower.endswith(".generated.py")
            or name_lower.endswith(".pb2.py")
            or "__pycache__" in file_path.parts
            or ".git" in file_path.parts
        )

    def _get_cache_key(self, file_path: Path) -> str:
        """Generate cache key for file."""
        return self.cache_manager.get_cache_key(
            str(file_path), self.output_config.get("include_architecture", True)
        )

    def _create_template_context(
        self,
        file_path: Path,
        code_content: str,
        documentation: str,
        architecture_description: str,
    ) -> Dict[str, Any]:
        """Create template context for rendering."""
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "language": self._detect_language(file_path.suffix),
            "documentation": documentation,
            "architecture_description": architecture_description,
            "include_architecture": self.output_config.get(
                "include_architecture", True
            ),
            "include_code_stats": self.output_config.get("include_code_stats", True),
            "include_dependencies": self.output_config.get(
                "include_dependencies", True
            ),
            "include_examples": self.output_config.get("include_examples", True),
            "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_info": self.model.get_model_info(),
            "code_stats": {
                "lines": len(code_content.splitlines()),
                "characters": len(code_content),
                "size_kb": round(len(code_content.encode("utf-8")) / 1024, 2),
            },
            "config": {
                "detail_level": self.generation_config.get("detail_level", "medium"),
                "author": self.config.get("templates", {}).get("author", ""),
                "organization": self.config.get("templates", {}).get(
                    "organization", ""
                ),
                "project_name": self.config.get("templates", {}).get(
                    "project_name", ""
                ),
                "version": self.config.get("templates", {}).get("version", "1.0.0"),
            },
        }

    def _save_documentation(self, input_file: Path, content: str) -> str:
        """Save generated documentation to file."""
        output_dir = Path(self.output_config.get("dir", "output"))
        filename_template = self.output_config.get(
            "filename_template", "{name}_documentation.md"
        )

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        output_filename = filename_template.format(
            name=input_file.stem, original_filename=input_file.name
        )

        # Preserve directory structure if configured
        if self.output_config.get("preserve_structure", True):
            # Calculate relative path from current working directory
            try:
                rel_path = input_file.relative_to(Path.cwd())
                output_subdir = output_dir / rel_path.parent
                output_subdir.mkdir(parents=True, exist_ok=True)
                output_path = output_subdir / output_filename
            except ValueError:
                # File is not relative to cwd, use flat structure
                output_path = output_dir / output_filename
        else:
            output_path = output_dir / output_filename

        # Save content
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(output_path)

    def _generate_directory_summary(
        self, dir_path: Path, result_files: List[str]
    ) -> Optional[str]:
        """Generate a summary document for the directory."""
        try:
            output_dir = Path(self.output_config.get("dir", "output"))
            summary_filename = f"{dir_path.name}_summary.md"
            summary_path = output_dir / summary_filename

            # Create summary content
            summary_content = f"""# Documentation Summary: {dir_path.name}

Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Processed Files

"""

            for result_file in result_files:
                rel_path = Path(result_file).name
                summary_content += f"- [{rel_path}](./{rel_path})\n"

            summary_content += f"""

## Statistics

- Total files processed: {len(result_files)}
- Generated documentation files: {len(result_files)}

## Model Information

- Model: {self.model.get_model_info()['model_path']}
- Backend: {self.model.get_model_info()['backend']}
- Platform: {self.model.get_model_info()['platform']}

---

*Generated by DocGenAI*
"""

            # Save summary
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_content)

            logger.info(f"📋 Directory summary saved: {summary_path}")
            return str(summary_path)

        except Exception as e:
            logger.error(f"❌ Failed to generate directory summary: {str(e)}")
            return None

    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension."""
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
            ".R": "r",
        }
        return language_map.get(file_extension.lower(), "text")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache_manager.get_stats()

    def clear_cache(self):
        """Clear all cached data."""
        self.cache_manager.clear_cache()


# Convenience functions for backward compatibility
def generate_documentation(
    file_path: str,
    output_dir: str = "output",
    config: Optional[Dict[str, Any]] = None,
    include_architecture: bool = True,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Generate documentation for a single file (convenience function).

    Args:
        file_path: Path to source file
        output_dir: Output directory
        config: Configuration dictionary
        include_architecture: Include architecture analysis
        verbose: Enable verbose logging

    Returns:
        Generation result dictionary
    """
    from .models import create_model

    if config is None:
        from .config import load_config

        config = load_config()

    # Override output directory
    config["output"]["dir"] = output_dir
    config["output"]["include_architecture"] = include_architecture

    # Create model and generator
    model = create_model(config)
    generator = DocumentationGenerator(model, config)

    # Process file
    result_path = generator.process_file(Path(file_path))

    return {"output_file": result_path, "success": result_path is not None}


def generate_directory_documentation(
    dir_path: str,
    output_dir: str = "output",
    config: Optional[Dict[str, Any]] = None,
    include_architecture: bool = True,
    file_patterns: Optional[List[str]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Generate documentation for a directory (convenience function).

    Args:
        dir_path: Path to source directory
        output_dir: Output directory
        config: Configuration dictionary
        include_architecture: Include architecture analysis
        file_patterns: File patterns to process
        verbose: Enable verbose logging

    Returns:
        Generation result dictionary
    """
    from .models import create_model

    if config is None:
        from .config import load_config

        config = load_config()

    # Override configuration
    config["output"]["dir"] = output_dir
    config["output"]["include_architecture"] = include_architecture
    if file_patterns:
        config["generation"]["file_patterns"] = file_patterns

    # Create model and generator
    model = create_model(config)
    generator = DocumentationGenerator(model, config)

    # Process directory
    results = generator.process_directory(Path(dir_path))

    return {
        "output_files": results,
        "files_processed": len(results),
        "success": len(results) > 0,
    }


def clean_documentation_output(content: str) -> str:
    """
    Clean up common formatting issues in generated documentation.

    Args:
        content: Raw documentation content

    Returns:
        Cleaned documentation content
    """
    # Remove spurious ```text markers
    content = re.sub(r"```text\s*\n", "\n", content)
    content = re.sub(r"```text\s*$", "", content, flags=re.MULTILINE)

    # Fix malformed patterns like **Documentation**: followed by ```
    content = re.sub(r"\*\*Documentation\*\*:\s*\n```\s*\n", "", content)

    # Fix Mermaid syntax issues with quotes in node labels
    def fix_mermaid_quotes(match):
        mermaid_content = match.group(1)

        # Simplify node labels by removing quotes and special characters
        lines = mermaid_content.split("\n")
        fixed_lines = []
        for line in lines:
            if "-->" in line and "[" in line and "]" in line:
                # Remove all quotes from node labels
                line = re.sub(r'(\w+)\["([^"]*)"\]', r"\1[\2]", line)

                # Clean up node labels: remove problematic characters and replace spaces
                def clean_label(match):
                    label = match.group(2)
                    # Remove quotes, commas, exclamation marks, etc.
                    label = re.sub(r'[",!?;:\\]', "", label)
                    # Replace spaces with underscores
                    label = label.replace(" ", "_")
                    # Remove any remaining problematic characters
                    label = re.sub(r"[^\w_-]", "", label)
                    return f"{match.group(1)}[{label}]"

                line = re.sub(r"(\w+)\[([^\]]+)\]", clean_label, line)
            fixed_lines.append(line)

        mermaid_content = "\n".join(fixed_lines)
        return f"```mermaid\n{mermaid_content}\n```"

    # Apply quote fixes to mermaid blocks
    content = re.sub(
        r"```mermaid\s*\n(.*?)\n\s*```", fix_mermaid_quotes, content, flags=re.DOTALL
    )

    # Fix unclosed code blocks (all types: mermaid, python, bash, etc.)
    lines = content.split("\n")
    fixed_lines = []
    in_code_block = False
    code_block_type = None

    for i, line in enumerate(lines):
        # Check if starting a code block
        if line.strip().startswith("```") and not in_code_block:
            in_code_block = True
            code_block_type = line.strip()[3:].strip()  # Get the language after ```
            fixed_lines.append(line)
        # Check if ending a code block
        elif line.strip() == "```" and in_code_block:
            in_code_block = False
            code_block_type = None
            fixed_lines.append(line)
        # Check if we hit a new section while in a code block
        elif in_code_block and (
            line.startswith("##")
            or line.startswith("**")
            or line.startswith("---")
            or (i == len(lines) - 1)
        ):
            # Close the code block before the new section
            fixed_lines.append("```")
            in_code_block = False
            code_block_type = None
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    # If we're still in a code block at the end, close it
    if in_code_block:
        fixed_lines.append("```")

    content = "\n".join(fixed_lines)

    # Remove duplicate empty lines
    content = re.sub(r"\n\n\n+", "\n\n", content)

    # Remove trailing whitespace
    content = "\n".join(line.rstrip() for line in content.split("\n"))

    return content
