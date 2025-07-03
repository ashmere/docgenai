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

from . import __version__
from .cache import CacheManager
from .chaining import PromptChain
from .config import (
    get_cache_config,
    get_generation_config,
    get_model_config,
    get_output_config,
    load_config,
)
from .models import AIModel
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
        self.chaining_config = config.get("chaining", {})

        # Initialize components
        self.cache_manager = CacheManager(self.cache_config)
        self.template_manager = TemplateManager(config.get("templates", {}))

        logger.info("🚀 DocumentationGenerator initialized")
        logger.info(f"📋 Model: {self.model.get_model_info()['model_path']}")
        logger.info(f"⚙️  Backend: {self.model.get_model_info()['backend']}")

        # Log chaining status
        chaining_enabled = self.chaining_config.get("enabled", False)
        if chaining_enabled:
            strategy = self.chaining_config.get("default_strategy", "simple")
            logger.info(f"🔗 Chaining enabled: {strategy} strategy")
        else:
            logger.info("📝 Using single-step generation (chaining disabled)")

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
                # Regenerate output file in current output directory
                cached_doc = cached_result.get("documentation", "")
                cached_arch = cached_result.get("architecture_description", "")

                # Create analysis info for single file
                analysis_info = {
                    "multi_file": False,
                    "project_type": "auto",
                    "doc_type": "both",
                    "file_count": 1,
                    "groups": 1,
                    "synthesis_used": False,
                    "chaining_enabled": False,
                    "chain_strategy": "single_file",
                    "chain_steps": 1,
                    "chain_description": "Single file documentation",
                    "post_processing": True,
                }

                # Create context for current output directory
                context = self._create_template_context(
                    file_path, "", cached_doc, cached_arch, analysis_info
                )

                # Render template
                rendered_doc = self.template_manager.render_documentation(context)
                rendered_doc = clean_documentation_output(rendered_doc)

                # Save to current output directory
                output_path = self._save_documentation(file_path, rendered_doc)
                logger.info(f"💾 Regenerated cached result to: {output_path}")
                return output_path

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
                )
                arch_elapsed = time.time() - arch_start
                logger.info(
                    f"✅ Architecture description generated in "
                    f"{arch_elapsed:.2f} seconds"
                )

            # Create analysis info for single file
            analysis_info = {
                "multi_file": False,
                "project_type": "auto",
                "doc_type": "both",
                "file_count": 1,
                "groups": 1,
                "synthesis_used": False,
                "chaining_enabled": False,
                "chain_strategy": "single_file",
                "chain_steps": 1,
                "chain_description": "Single file documentation",
                "post_processing": True,
            }

            # Prepare template context
            context = self._create_template_context(
                file_path,
                code_content,
                documentation,
                architecture_description,
                analysis_info,
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

        # Always generate index for navigation
        if self.output_config.get("create_subdirs", True) and results:
            index_path = self._generate_index(dir_path)
            if index_path:
                results.append(index_path)

            # Generate comprehensive summary only if chaining is enabled
            chaining_config = self.config.get("chaining", {})
            if chaining_config.get("enabled", False):
                summary_path = self._generate_summary(dir_path, results)
                if summary_path:
                    results.append(summary_path)

        total_elapsed = time.time() - start_time
        logger.info(f"🎉 Directory processing complete in {total_elapsed:.2f} seconds")
        logger.info(f"📊 Results: {successful} successful, {failed} failed")

        return results

    def execute_chain(
        self, chain: PromptChain, code_content: str, file_path: str
    ) -> Optional[str]:
        """
        Execute a prompt chain for documentation generation.

        Args:
            chain: PromptChain to execute
            code_content: Source code content
            file_path: Path to the source file

        Returns:
            Final documentation output, or None if failed
        """
        logger.info(f"🔗 Executing chain: {chain.name}")

        # Prepare initial inputs
        initial_inputs = {
            "code": code_content,
            "file_path": file_path,
            "language": self._detect_language(Path(file_path).suffix),
        }

        # Create model function for the chain
        def model_fn(prompt: str) -> str:
            return self.model.generate_raw_response(prompt)

        # Execute the chain
        context = chain.execute(model_fn, initial_inputs)

        # Check for successful completion
        if context.failure_count > 0:
            failed_steps = context.get_failed_steps()
            logger.warning(
                f"⚠️  Chain had {context.failure_count} failed steps: " f"{failed_steps}"
            )

            # If fail_fast is enabled and we have failures, return None
            if chain.fail_fast and context.failure_count > 0:
                logger.error("❌ Chain execution failed (fail_fast=True)")
                return None

        # Get the final output
        # For simple chains, use the last successful step
        # For complex chains, look for specific output steps
        all_outputs = context.get_all_outputs()

        if not all_outputs:
            logger.error("❌ No successful outputs from chain")
            return None

        # Determine which output to use
        if "combined_documentation" in all_outputs:
            final_output = all_outputs["combined_documentation"]
        elif "enhance" in all_outputs:
            final_output = all_outputs["enhance"]
        elif "documentation" in all_outputs:
            final_output = all_outputs["documentation"]
        else:
            # Use the last successful output
            final_output = list(all_outputs.values())[-1]

        logger.info(
            f"✅ Chain execution completed: {context.success_count} "
            f"successful steps"
        )
        return final_output

    def _load_ignore_patterns(self, dir_path: Path) -> List[str]:
        """Load ignore patterns from .docgenai_ignore file."""
        # Look for .docgenai_ignore in the current working directory first,
        # then in the target directory
        ignore_locations = [
            Path.cwd() / ".docgenai_ignore",
            dir_path / ".docgenai_ignore",
        ]

        patterns = []
        ignore_file = None

        for location in ignore_locations:
            if location.exists():
                ignore_file = location
                break

        if ignore_file:
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
        analysis_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create template context for rendering."""
        context = {
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
                "docgenai_version": __version__,
                "project_version": self.config.get("templates", {}).get(
                    "project_version", ""
                ),
            },
        }

        # Add analysis_info if provided
        if analysis_info:
            context["analysis_info"] = analysis_info

        return context

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

    def _generate_index(self, dir_path: Path) -> Optional[str]:
        """Generate an index document for all documentation in the output directory."""
        try:
            output_dir = Path(self.output_config.get("dir", "output"))
            index_path = output_dir / "index.md"

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Find all markdown files in the output directory
            all_docs = []
            if output_dir.exists():
                for md_file in output_dir.glob("*.md"):
                    if md_file.name != "index.md":  # Don't include the index itself
                        all_docs.append(md_file)

            # Sort by name for consistent ordering
            all_docs.sort(key=lambda x: x.name)

            # Create index content
            index_content = f"""# Documentation Index

Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Available Documentation

"""

            if all_docs:
                for doc_file in all_docs:
                    # Create a readable name from filename
                    display_name = doc_file.stem.replace("_", " ").title()
                    if display_name.endswith(" Documentation"):
                        # Remove " Documentation" suffix
                        display_name = display_name[:-14]

                    index_content += f"- [{display_name}](./{doc_file.name})\n"
            else:
                index_content += "*No documentation files found.*\n"

            index_content += f"""

## Statistics

- Total documentation files: {len(all_docs)}
- Last updated: {time.strftime("%Y-%m-%d %H:%M:%S")}

---

*Generated by DocGenAI*
"""

            # Apply post-processing to clean up formatting
            index_content = clean_documentation_output(index_content)

            # Save index
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)

            logger.info(f"📋 Documentation index saved: {index_path}")
            return str(index_path)

        except Exception as e:
            logger.error(f"❌ Failed to generate documentation index: {str(e)}")
            return None

    def _generate_summary(
        self, dir_path: Path, result_files: List[str]
    ) -> Optional[str]:
        """Generate a comprehensive architectural summary using prompt chaining."""
        try:
            output_dir = Path(self.output_config.get("dir", "output"))
            summary_path = output_dir / "summary.md"

            # Collect all source code content for analysis
            source_files = self._find_source_files(dir_path)
            all_code_content = {}

            # Limit to first 10 files to avoid token limits
            for file_path in source_files[:10]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        rel_path = str(file_path.relative_to(dir_path))
                        all_code_content[rel_path] = content
                except Exception as e:
                    logger.warning(f"⚠️  Could not read {file_path}: {e}")
                    continue

            if not all_code_content:
                logger.warning(
                    "⚠️  No source code content available for summary generation"
                )
                return None

            # Determine chain strategy - prefer architecture, fallback to enhanced
            chaining_config = self.config.get("chaining", {})
            strategy = chaining_config.get("default_strategy", "enhanced")
            if strategy == "simple":
                strategy = "enhanced"  # Upgrade simple to enhanced for summary

            # Create appropriate chain for summary generation
            from .chaining import ChainBuilder

            builder = ChainBuilder()

            if strategy == "architecture":
                chain = builder.architecture_diagram_chain()
            else:
                chain = builder.enhanced_documentation_chain()

            # Prepare combined code content for chain input
            combined_content = f"""# Codebase Overview: {dir_path.name}

## Project Structure
Files analyzed: {len(all_code_content)}

"""

            for file_path, content in all_code_content.items():
                # Truncate very long files to avoid token limits
                truncated_content = (
                    content[:2000] + "..." if len(content) > 2000 else content
                )
                combined_content += f"""
## {file_path}

```{self._detect_language(Path(file_path).suffix)}
{truncated_content}
```

"""

            # Execute chain for summary generation
            logger.info(
                f"🔗 Generating architectural summary using {strategy} strategy"
            )
            summary_documentation = self.execute_chain(
                chain, combined_content, str(dir_path)
            )

            if not summary_documentation:
                logger.error("❌ Failed to generate summary using prompt chaining")
                return None

            # Apply post-processing to clean up formatting
            summary_documentation = clean_documentation_output(summary_documentation)

            # Save summary
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_documentation)

            logger.info(f"📋 Architectural summary saved: {summary_path}")
            return str(summary_path)

        except Exception as e:
            logger.error(f"❌ Failed to generate architectural summary: {str(e)}")
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
    target_path: Path,
    output_dir: str = "output",
    template_file: Optional[str] = None,
    style_guide_file: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    diagrams: bool = False,
) -> Dict[str, Any]:
    """
    Generate documentation for files or directories with multi-file support.

    Args:
        target_path: Path to source file or directory
        output_dir: Output directory
        template_file: Custom template file path
        style_guide_file: Custom style guide file path
        config: Configuration dictionary
        diagrams: Include diagrams in documentation

    Returns:
        Generation result dictionary
    """
    from .chaining.context import ChainContext
    from .models import create_model

    # Choose analyzer based on config
    use_enhanced = (
        config.get("documentation", {}).get("use_enhanced_analyzer", False)
        if config
        else False
    )

    if use_enhanced:
        from .enhanced_multi_file_analyzer import (
            EnhancedMultiFileAnalyzer as MultiFileAnalyzer,
        )
    else:
        from .multi_file_analyzer import MultiFileAnalyzer

    if config is None:
        config = load_config()

    # Override output directory
    config["output"]["dir"] = output_dir

    # Handle custom template and style guide
    if template_file:
        config["templates"]["template_file"] = template_file
    if style_guide_file:
        config["templates"]["style_guide_file"] = style_guide_file

    # Handle diagrams
    config["output"]["include_diagrams"] = diagrams

    # Check if multi-file mode is enabled
    multi_file_config = config.get("multi_file", {})
    multi_file_enabled = multi_file_config.get("enabled", False)

    logger.info(f"🎯 Target: {target_path}")
    logger.info(f"📁 Output: {output_dir}")
    logger.info(f"🔗 Multi-file: {multi_file_enabled}")

    # Create model
    model = create_model(config)

    if target_path.is_file() and not multi_file_enabled:
        # Single file mode (existing behavior)
        generator = DocumentationGenerator(model, config)
        result_path = generator.process_file(target_path)
        return {
            "output_files": [result_path] if result_path else [],
            "success": result_path is not None,
        }

    elif target_path.is_dir() and multi_file_enabled:
        # Multi-file directory analysis
        return _generate_multi_file_documentation(
            target_path, model, config, output_dir
        )

    elif target_path.is_file() and multi_file_enabled:
        # Single file with multi-file context (analyze related files)
        parent_dir = target_path.parent
        return _generate_multi_file_documentation(
            parent_dir, model, config, output_dir, focus_file=target_path
        )

    else:
        # Fallback to directory mode
        generator = DocumentationGenerator(model, config)
        results = generator.process_directory(target_path)
        return {
            "output_files": results,
            "success": len(results) > 0,
        }


def _generate_multi_file_documentation(
    target_path: Path,
    model: AIModel,
    config: Dict[str, Any],
    output_dir: str,
    focus_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Generate documentation using multi-file analysis.

    Args:
        target_path: Directory to analyze
        model: AI model instance
        config: Configuration
        output_dir: Output directory
        focus_file: Optional file to focus on

    Returns:
        Generation result dictionary
    """
    from .chaining.context import ChainContext

    # Choose analyzer based on config
    use_enhanced = config.get("documentation", {}).get("use_enhanced_analyzer", False)

    if use_enhanced:
        from .enhanced_multi_file_analyzer import (
            EnhancedMultiFileAnalyzer as MultiFileAnalyzer,
        )
    else:
        from .multi_file_analyzer import MultiFileAnalyzer

    logger.info("🔗 Starting multi-file analysis...")

    # Initialize analyzer with model for automatic token detection
    if use_enhanced:
        analyzer = MultiFileAnalyzer(config, model)
    else:
        analyzer = MultiFileAnalyzer(config)

    # Analyze codebase structure
    codebase_structure = analyzer.analyze_codebase_structure(target_path)

    logger.info(f"📊 Codebase structure:")
    logger.info(f"  - Total files: {codebase_structure['total_files']}")
    logger.info(f"  - Analysis groups: {codebase_structure['groups']}")
    logger.info(f"  - Requires synthesis: {codebase_structure['requires_synthesis']}")

    # Get chain strategy
    chain_strategy = config.get("chain_strategy", "multi_file")
    logger.info(f"🔗 Using chain strategy: {chain_strategy}")

    # Handle different strategies
    if codebase_structure["groups"] == 0:
        logger.warning("⚠️  No suitable files found for analysis")
        return {"output_files": [], "success": False, "error": "No suitable files"}

    elif codebase_structure["groups"] == 1:
        # Single group - use specified strategy
        return _analyze_single_group(
            analyzer, model, config, output_dir, codebase_structure, chain_strategy
        )

    else:
        # Multiple groups - use codebase analysis with synthesis
        return _analyze_multiple_groups(
            analyzer, model, config, output_dir, codebase_structure, chain_strategy
        )


def _analyze_single_group(
    analyzer: "MultiFileAnalyzer",
    model: AIModel,
    config: Dict[str, Any],
    output_dir: str,
    codebase_structure: Dict[str, Any],
    chain_strategy: str,
) -> Dict[str, Any]:
    """Analyze a single group of files."""
    from .chaining.context import ChainContext

    logger.info("📝 Analyzing single file group...")

    # Get the group
    source_files = analyzer._find_source_files(Path(codebase_structure["root_path"]))
    groups = analyzer.group_files_for_analysis(source_files)

    if not groups:
        return {"output_files": [], "success": False, "error": "No groups found"}

    file_group = groups[0]

    # Prepare context
    context = analyzer.prepare_multi_file_context(file_group)

    # Get documentation configuration
    doc_config = config.get("documentation", {})
    doc_type = doc_config.get("doc_type", "developer")
    project_type = context.get("project_type", "auto")

    # Create chain with specified strategy (only multi_file and codebase work with multi-file analysis)
    from .chaining.builders import ChainBuilder

    multi_file_compatible_strategies = ["multi_file", "codebase"]
    if chain_strategy not in multi_file_compatible_strategies:
        logger.warning(
            f"⚠️  Strategy '{chain_strategy}' not compatible with multi-file analysis, using 'multi_file'"
        )
        chain_strategy = "multi_file"

    chain = ChainBuilder.create_chain(
        chain_strategy, doc_type=doc_type, project_type=project_type
    )

    # Execute chain
    chain_context = ChainContext()
    chain_context.set_input("files_content", context["files_content"])
    chain_context.set_input("files_summary", context["files_summary"])
    chain_context.set_input("file_count", context["file_count"])
    chain_context.set_input("file_names", context["file_names"])
    chain_context.set_input("project_type", project_type)
    # Add variables needed by codebase strategy
    chain_context.set_input("total_files", context["file_count"])
    chain_context.set_input("total_size", context.get("total_size", 0))
    chain_context.set_input("primary_language", "python")  # Default fallback
    chain_context.set_input("groups", 1)  # Single group for this strategy

    # Execute steps
    for step in chain.steps:
        try:
            prompt = step.build_prompt(chain_context)
            response = model.generate_raw_response(prompt)

            # Store result
            from .chaining.context import StepResult

            result = StepResult(
                step_name=step.name, output=response, execution_time=0.0
            )
            chain_context.add_result(result)

            # Add to inputs for next step
            chain_context.set_input(step.name, response)

        except Exception as e:
            logger.error(f"❌ Step {step.name} failed: {e}")
            continue

    # Get final documentation
    final_docs = chain_context.get_output("multi_file_documentation")
    if not final_docs:
        return {
            "output_files": [],
            "success": False,
            "error": "Documentation generation failed",
        }

    # Create analysis_info for template context
    analysis_info = {
        "multi_file": True,
        "project_type": project_type,
        "doc_type": doc_type,
        "file_count": len(file_group),
        "groups": 1,
        "synthesis_used": False,
        "chaining_enabled": True,
        "chain_strategy": chain_strategy,
        "chain_steps": len(chain.steps),
        "chain_description": f"Multi-file analysis for {project_type} project",
        "post_processing": True,
    }

    # Create template manager and render with footer
    template_manager = TemplateManager(config.get("templates", {}))

    # Create template context for the first file (representative)
    first_file_path = Path(file_group[0])
    template_context = {
        "file_path": str(first_file_path.parent),
        "file_name": "Multi-file Analysis",
        "language": "Multiple",
        "documentation": final_docs,
        "architecture_description": "",
        "include_architecture": False,
        "include_code_stats": True,
        "include_dependencies": True,
        "include_examples": True,
        "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_info": model.get_model_info(),
        "code_stats": {
            "lines": sum(
                len(open(f, "r", encoding="utf-8", errors="ignore").read().splitlines())
                for f in file_group
            ),
            "characters": sum(
                len(open(f, "r", encoding="utf-8", errors="ignore").read())
                for f in file_group
            ),
            "size_kb": round(
                sum(
                    len(
                        open(f, "r", encoding="utf-8", errors="ignore")
                        .read()
                        .encode("utf-8")
                    )
                    for f in file_group
                )
                / 1024,
                2,
            ),
        },
        "analysis_info": analysis_info,
        "config": {
            "detail_level": config.get("generation", {}).get("detail_level", "medium"),
            "author": config.get("templates", {}).get("author", ""),
            "organization": config.get("templates", {}).get("organization", ""),
            "project_name": config.get("templates", {}).get("project_name", ""),
            "docgenai_version": __version__,
            "project_version": config.get("templates", {}).get("project_version", ""),
        },
    }

    # Render footer
    footer_content = template_manager.render_footer(template_context)

    # Save output with template footer
    output_path = Path(output_dir) / "multi_file_documentation.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Multi-File Documentation\n\n")
        f.write(f"**Files analyzed:** {', '.join(context['file_names'])}\n\n")
        f.write("---\n\n")
        f.write(clean_documentation_output(final_docs))
        f.write("\n\n")
        f.write(footer_content)

    logger.info(f"✅ Multi-file documentation saved: {output_path}")

    # Generate index.md for the output directory
    output_files = [str(output_path)]
    try:
        index_path = _generate_index_standalone(output_dir)
        if index_path:
            output_files.append(index_path)
    except Exception as e:
        logger.warning(f"⚠️  Failed to generate index: {e}")

    return {
        "output_files": output_files,
        "success": True,
        "multi_file_stats": {
            "groups": 1,
            "total_files": len(file_group),
            "synthesis_used": False,
        },
    }


def _analyze_multiple_groups(
    analyzer: "MultiFileAnalyzer",
    model: AIModel,
    config: Dict[str, Any],
    output_dir: str,
    codebase_structure: Dict[str, Any],
    chain_strategy: str,
) -> Dict[str, Any]:
    """Analyze multiple groups with synthesis."""
    from .chaining.context import ChainContext

    logger.info(
        f"🏗️  Analyzing {codebase_structure['groups']} file groups with synthesis..."
    )

    # Get all groups
    source_files = analyzer._find_source_files(Path(codebase_structure["root_path"]))
    groups = analyzer.group_files_for_analysis(source_files)

    # Create group summaries
    group_summaries = analyzer.create_group_summaries(groups)

    # Prepare synthesis context
    primary_directories = list(set(s["primary_directory"] for s in group_summaries))
    large_files_info = (
        "\n".join(
            [
                f"- {lf['file']} ({lf['size']} chars): {lf['reason']}"
                for lf in codebase_structure["large_files"]
            ]
        )
        if codebase_structure["large_files"]
        else "None"
    )

    group_summaries_text = "\n".join(
        [
            f"**Group {s['group_id']}** ({s['primary_directory']}):\n"
            f"  - Files: {', '.join(s['files'])}\n"
            f"  - Components: {', '.join(s['key_components'][:5])}\n"
            f"  - Tokens: {s['estimated_tokens']:.0f}\n"
            for s in group_summaries
        ]
    )

    # Get documentation configuration
    doc_config = config.get("documentation", {})
    doc_type = doc_config.get("doc_type", "developer")
    project_type = doc_config.get("project_type", "auto")

    # Create chain with specified strategy (fallback to codebase for multi-group)
    from .chaining.builders import ChainBuilder

    # Use the specified chain strategy, fallback to codebase for complex multi-group analysis
    effective_strategy = chain_strategy
    chain = ChainBuilder.create_chain(
        effective_strategy, doc_type=doc_type, project_type=project_type
    )

    # Execute chain
    chain_context = ChainContext()
    chain_context.set_input("total_files", codebase_structure["total_files"])
    chain_context.set_input("groups", codebase_structure["groups"])
    chain_context.set_input("primary_directories", ", ".join(primary_directories))
    chain_context.set_input("group_summaries", group_summaries_text)
    chain_context.set_input("large_files", large_files_info)

    # Execute steps
    for step in chain.steps:
        try:
            prompt = step.build_prompt(chain_context)
            response = model.generate_raw_response(prompt)

            # Store result
            from .chaining.context import StepResult

            result = StepResult(
                step_name=step.name, output=response, execution_time=0.0
            )
            chain_context.add_result(result)

            # Add to inputs for next step
            chain_context.set_input(step.name, response)

        except Exception as e:
            logger.error(f"❌ Step {step.name} failed: {e}")
            continue

    # Get final documentation
    final_docs = chain_context.get_output("comprehensive_documentation")
    if not final_docs:
        return {"output_files": [], "success": False, "error": "Synthesis failed"}

    # Create output structure
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create analysis_info for template context
    analysis_info = {
        "multi_file": True,
        "project_type": project_type,
        "doc_type": doc_type,
        "file_count": codebase_structure["total_files"],
        "groups": codebase_structure["groups"],
        "synthesis_used": True,
        "chaining_enabled": True,
        "chain_strategy": effective_strategy,
        "chain_steps": len(chain.steps),
        "chain_description": f"Multi-group synthesis for {project_type} project",
        "post_processing": True,
        "total_tokens": sum(s["estimated_tokens"] for s in group_summaries),
    }

    # Create template manager and render with footer
    template_manager = TemplateManager(config.get("templates", {}))

    # Create template context
    template_context = {
        "file_path": codebase_structure["root_path"],
        "file_name": "Codebase Analysis",
        "language": "Multiple",
        "documentation": final_docs,
        "architecture_description": "",
        "include_architecture": False,
        "include_code_stats": True,
        "include_dependencies": True,
        "include_examples": True,
        "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_info": model.get_model_info(),
        "code_stats": {
            "lines": 0,  # Will be calculated from group summaries
            "characters": 0,  # Will be calculated from group summaries
            "size_kb": 0,  # Will be calculated from group summaries
        },
        "analysis_info": analysis_info,
        "config": {
            "detail_level": config.get("generation", {}).get("detail_level", "medium"),
            "author": config.get("templates", {}).get("author", ""),
            "organization": config.get("templates", {}).get("organization", ""),
            "project_name": config.get("templates", {}).get("project_name", ""),
            "docgenai_version": __version__,
            "project_version": config.get("templates", {}).get("project_version", ""),
        },
    }

    # Render footer
    footer_content = template_manager.render_footer(template_context)

    # Save comprehensive documentation
    main_doc_path = output_path / "codebase_documentation.md"
    with open(main_doc_path, "w", encoding="utf-8") as f:
        f.write("# Codebase Documentation\n\n")
        f.write(f"**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Files:** {codebase_structure['total_files']}\n\n")
        f.write(f"**Analysis Groups:** {codebase_structure['groups']}\n\n")
        f.write("---\n\n")
        f.write(clean_documentation_output(final_docs))
        f.write("\n\n")
        f.write(footer_content)

    # Save individual group documentation
    output_files = [str(main_doc_path)]

    for i, group in enumerate(groups):
        if len(group) > 0:
            try:
                # Generate individual group documentation
                context = analyzer.prepare_multi_file_context(group)
                group_chain = ChainBuilder.multi_file_analysis_chain(
                    doc_type=doc_type, project_type=project_type
                )

                group_context = ChainContext()
                group_context.set_input("files_content", context["files_content"])
                group_context.set_input("files_summary", context["files_summary"])
                group_context.set_input("file_count", context["file_count"])
                group_context.set_input("file_names", context["file_names"])
                group_context.set_input(
                    "project_type", context.get("project_type", project_type)
                )

                # Execute group analysis
                for step in group_chain.steps:
                    try:
                        prompt = step.build_prompt(group_context)
                        response = model.generate_raw_response(prompt)

                        from .chaining.context import StepResult

                        result = StepResult(
                            step_name=step.name, output=response, execution_time=0.0
                        )
                        group_context.add_result(result)
                        group_context.set_input(step.name, response)

                    except Exception as e:
                        logger.warning(f"⚠️  Group {i+1} step {step.name} failed: {e}")
                        continue

                # Save group documentation
                group_docs = group_context.get_output("comprehensive_documentation")
                if group_docs:
                    group_path = output_path / f"group_{i+1}_documentation.md"
                    with open(group_path, "w", encoding="utf-8") as f:
                        f.write(f"# Group {i+1} Documentation\n\n")
                        f.write(f"**Files:** {', '.join(context['file_names'])}\n\n")
                        f.write("---\n\n")
                        f.write(clean_documentation_output(group_docs))

                    output_files.append(str(group_path))
                    logger.info(f"📄 Group {i+1} documentation saved: {group_path}")

            except Exception as e:
                logger.warning(f"⚠️  Failed to generate group {i+1} documentation: {e}")

    logger.info(f"✅ Codebase analysis complete: {len(output_files)} files generated")

    # Generate index.md for the output directory
    try:
        index_path = _generate_index_standalone(output_dir)
        if index_path:
            output_files.append(index_path)
    except Exception as e:
        logger.warning(f"⚠️  Failed to generate index: {e}")

    return {
        "output_files": output_files,
        "success": True,
        "multi_file_stats": {
            "groups": codebase_structure["groups"],
            "total_files": codebase_structure["total_files"],
            "synthesis_used": True,
        },
    }


def generate_single_file_documentation(
    file_path: str,
    output_dir: str = "output",
    config: Optional[Dict[str, Any]] = None,
    include_architecture: bool = True,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Generate documentation for a single file (backward compatibility).

    Args:
        file_path: Path to source file
        output_dir: Output directory
        config: Configuration dictionary
        include_architecture: Include architecture analysis
        verbose: Enable verbose logging

    Returns:
        Generation result dictionary
    """
    if config is None:
        config = load_config()

    # Override output directory
    config["output"]["dir"] = output_dir
    config["output"]["include_architecture"] = include_architecture

    # Disable multi-file mode for backward compatibility
    config["multi_file"] = {"enabled": False}

    # Use the new function
    result = generate_documentation(
        target_path=Path(file_path),
        output_dir=output_dir,
        config=config,
    )

    # Convert to old format
    output_files = result.get("output_files", [])
    return {
        "output_file": output_files[0] if output_files else None,
        "success": result.get("success", False),
    }


def generate_directory_documentation(
    dir_path: str,
    output_dir: str = "output",
    config: Optional[Dict[str, Any]] = None,
    include_architecture: bool = True,
    file_patterns: Optional[List[str]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Generate documentation for a directory (backward compatibility).

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
    if config is None:
        config = load_config()

    # Override configuration
    config["output"]["dir"] = output_dir
    config["output"]["include_architecture"] = include_architecture
    if file_patterns:
        config["generation"]["file_patterns"] = file_patterns

    # Disable multi-file mode for backward compatibility
    config["multi_file"] = {"enabled": False}

    # Use the new function
    result = generate_documentation(
        target_path=Path(dir_path),
        output_dir=output_dir,
        config=config,
    )

    return {
        "output_files": result.get("output_files", []),
        "files_processed": len(result.get("output_files", [])),
        "success": result.get("success", False),
    }


def _generate_index_standalone(output_dir: str) -> Optional[str]:
    """Generate an index document for all documentation in the output directory."""
    try:
        import time

        output_path = Path(output_dir)
        index_path = output_path / "index.md"

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all markdown files in the output directory
        all_docs = []
        if output_path.exists():
            for md_file in output_path.glob("*.md"):
                if md_file.name != "index.md":  # Don't include the index itself
                    all_docs.append(md_file)

        # Sort by name for consistent ordering
        all_docs.sort(key=lambda x: x.name)

        # Create index content
        index_content = f"""# Documentation Index

Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Available Documentation

"""

        if all_docs:
            for doc_file in all_docs:
                # Create a readable name from filename
                display_name = doc_file.stem.replace("_", " ").title()
                if display_name.endswith(" Documentation"):
                    # Remove " Documentation" suffix
                    display_name = display_name[:-14]

                index_content += f"- [{display_name}](./{doc_file.name})\n"
        else:
            index_content += "*No documentation files found.*\n"

        index_content += f"""

## Statistics

- Total documentation files: {len(all_docs)}
- Last updated: {time.strftime("%Y-%m-%d %H:%M:%S")}

---

*Generated by DocGenAI*
"""

        # Apply post-processing to clean up formatting
        index_content = clean_documentation_output(index_content)

        # Save index
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

        logger.info(f"📋 Documentation index saved: {index_path}")
        return str(index_path)

    except Exception as e:
        logger.error(f"❌ Failed to generate documentation index: {str(e)}")
        return None


def clean_documentation_output(content: str) -> str:
    """
    Clean up common formatting issues in generated documentation.
    Fixes markdown linting issues to pass markdownlint checks.

    Args:
        content: Raw documentation content

    Returns:
        Cleaned documentation content
    """
    from .post_processing import process_generated_markdown

    return process_generated_markdown(content)


def _fix_markdown_linting_issues(content: str) -> str:
    """
    Fix specific markdown linting issues identified by markdownlint.

    Args:
        content: Markdown content to fix

    Returns:
        Fixed markdown content
    """
    # Fix unclosed code block transitions first
    content = _fix_unclosed_code_block_transitions(content)

    # Remove consecutive identical code blocks
    content = _remove_consecutive_identical_blocks(content)

    lines = content.split("\n")
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # MD031: Fenced code blocks should be surrounded by blank lines
        if line.strip().startswith("```"):
            # Ensure blank line before code block (unless it's the first line)
            if i > 0 and fixed_lines and fixed_lines[-1].strip() != "":
                fixed_lines.append("")

            fixed_lines.append(line)
            i += 1

            # Find the closing ``` and ensure blank line after
            while i < len(lines):
                current_line = lines[i]
                fixed_lines.append(current_line)

                if current_line.strip() == "```":
                    # Ensure blank line after code block (unless it's the last line)
                    if i + 1 < len(lines) and lines[i + 1].strip() != "":
                        fixed_lines.append("")
                    break
                i += 1

        # MD032: Lists should be surrounded by blank lines
        elif line.strip().startswith(("- ", "* ", "+ ")) or re.match(
            r"^\d+\. ", line.strip()
        ):
            # Ensure blank line before list (unless it's the first line)
            if i > 0 and fixed_lines and fixed_lines[-1].strip() != "":
                fixed_lines.append("")

            # Add the list item
            fixed_lines.append(line)

            # Look ahead to see if this is part of a multi-item list
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if (
                    next_line.strip().startswith(("- ", "* ", "+ "))
                    or re.match(r"^\d+\. ", next_line.strip())
                    or next_line.strip() == ""
                    or next_line.startswith("  ")
                ):  # Indented content (part of list item)
                    fixed_lines.append(next_line)
                    j += 1
                else:
                    break

            # Ensure blank line after list
            if j < len(lines) and lines[j].strip() != "":
                fixed_lines.append("")

            i = j - 1  # -1 because we'll increment at the end of the loop

        else:
            fixed_lines.append(line)

        i += 1

    content = "\n".join(fixed_lines)

    # MD050: Strong style - convert __text__ to **text**
    content = re.sub(r"__([^_]+)__", r"**\1**", content)

    # MD012: Multiple consecutive blank lines - replace with single blank line
    # This handles the specific issue seen in test_output/multi_file_demo.md
    content = re.sub(r"\n\n\n+", "\n\n", content)

    # Remove trailing whitespace from all lines
    content = "\n".join(line.rstrip() for line in content.split("\n"))

    # MD013: Line length - break long lines at reasonable points
    content = _fix_long_lines(content)

    return content


def _fix_unclosed_code_block_transitions(content: str) -> str:
    """
    Fix cases where code blocks transition to different types without proper
    closing.

    Example: ```bash...```python becomes ```bash...```\n```python

    Args:
        content: Markdown content to fix

    Returns:
        Content with proper code block transitions
    """
    # First, handle inline transitions like "```python" appearing in content
    # This pattern matches content ending with ```language
    pattern = r"(```\w+.*?)```(\w+)"

    def fix_inline_transition(match):
        first_part = match.group(1)
        second_language = match.group(2)
        return first_part + "```\n\n```" + second_language

    content = re.sub(pattern, fix_inline_transition, content, flags=re.DOTALL)

    # Now handle line-by-line transitions
    lines = content.split("\n")
    result_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line starts a code block
        if line.strip().startswith("```") and len(line.strip()) > 3:
            # This is a code block start (e.g., ```python, ```bash)
            block_type = line.strip()[3:]  # Get the language/type
            result_lines.append(line)
            i += 1

            # Look for the closing ``` or another code block start
            block_closed = False
            while i < len(lines):
                current_line = lines[i]

                # Check if this line starts another code block without
                # closing the current one
                is_code_start = current_line.strip().startswith("```")
                has_language = len(current_line.strip()) > 3
                if is_code_start and has_language and not block_closed:
                    # We found another code block start without closing
                    # the previous one
                    result_lines.append("```")  # Close the previous block
                    result_lines.append("")  # Add blank line
                    result_lines.append(current_line)  # Start new block
                    block_closed = True
                    i += 1
                    break
                elif current_line.strip() == "```":
                    # Found proper closing
                    result_lines.append(current_line)
                    block_closed = True
                    i += 1
                    break
                else:
                    # Regular content inside the block
                    result_lines.append(current_line)
                    i += 1

            # If we reached the end without closing, close the block
            if not block_closed:
                result_lines.append("```")
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)


def _remove_consecutive_identical_blocks(content: str) -> str:
    """
    Remove consecutive identical code blocks to fix AI generation loops.

    Args:
        content: Markdown content to fix

    Returns:
        Content with consecutive duplicates removed
    """
    lines = content.split("\n")
    result_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is the start of a code block
        if line.strip().startswith("```"):
            # Extract the current code block
            current_block_lines = [line]
            i += 1

            # Find the end of the current block
            block_closed = False
            while i < len(lines):
                current_line = lines[i]
                current_block_lines.append(current_line)

                if current_line.strip() == "```":
                    block_closed = True
                    i += 1
                    break
                i += 1

            # If block wasn't closed, close it
            if not block_closed:
                current_block_lines.append("```")

            current_block = "\n".join(current_block_lines)

            # Look ahead for consecutive identical blocks
            consecutive_count = 1
            j = i
            removed_count = 0

            while j < len(lines):
                # Skip empty lines
                while j < len(lines) and lines[j].strip() == "":
                    j += 1

                if j >= len(lines):
                    break

                # Check if the next block starts
                if not lines[j].strip().startswith("```"):
                    break

                # Extract the next block
                next_block_lines = [lines[j]]
                j += 1

                # Find the end of the next block
                next_block_closed = False
                while j < len(lines):
                    next_line = lines[j]
                    next_block_lines.append(next_line)

                    if next_line.strip() == "```":
                        next_block_closed = True
                        j += 1
                        break
                    j += 1

                # If next block wasn't closed, close it
                if not next_block_closed:
                    next_block_lines.append("```")

                next_block = "\n".join(next_block_lines)

                # Normalize whitespace and content for comparison
                current_norm = re.sub(r"\s+", " ", current_block.strip())
                next_norm = re.sub(r"\s+", " ", next_block.strip())

                # Also check for very similar content (80% similarity)
                similarity_threshold = 0.8
                if len(current_norm) > 0 and len(next_norm) > 0:
                    # Simple similarity check: count common characters
                    common_chars = sum(
                        1 for a, b in zip(current_norm, next_norm) if a == b
                    )
                    max_len = max(len(current_norm), len(next_norm))
                    similarity = common_chars / max_len if max_len > 0 else 0
                    is_similar = similarity >= similarity_threshold
                else:
                    is_similar = False

                # If blocks are identical or very similar, skip the next block
                if current_norm == next_norm or is_similar:
                    consecutive_count += 1
                    removed_count += 1
                    i = j  # Skip this duplicate block

                    # Skip empty lines after the duplicate
                    while i < len(lines) and lines[i].strip() == "":
                        i += 1
                else:
                    break

            # Add the first (non-duplicate) block to results
            result_lines.extend(current_block_lines)

            # Add a note if we removed duplicates
            if removed_count > 0:
                result_lines.append("")
                comment = f"<!-- Removed {removed_count} duplicate code blocks -->"
                result_lines.append(comment)
                result_lines.append("")
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)


def _fix_long_lines(content: str, max_length: int = 400) -> str:
    """
    Break long lines at reasonable points to fix MD013 line length issues.

    Args:
        content: Markdown content
        max_length: Maximum line length

    Returns:
        Content with long lines broken
    """
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) <= max_length:
            fixed_lines.append(line)
            continue

        # Don't break code blocks, headers, or URLs
        if (
            line.strip().startswith(("```", "#", "http://", "https://"))
            or "```" in line
        ):
            fixed_lines.append(line)
            continue

        # Try to break at sentence boundaries
        if ". " in line:
            parts = line.split(". ")
            current_line = parts[0]

            for part in parts[1:]:
                if len(current_line + ". " + part) <= max_length:
                    current_line += ". " + part
                else:
                    fixed_lines.append(current_line + ".")
                    current_line = part

            if current_line:
                fixed_lines.append(current_line)

        # Try to break at comma boundaries
        elif ", " in line:
            parts = line.split(", ")
            current_line = parts[0]

            for part in parts[1:]:
                if len(current_line + ", " + part) <= max_length:
                    current_line += ", " + part
                else:
                    fixed_lines.append(current_line + ",")
                    current_line = part

            if current_line:
                fixed_lines.append(current_line)

        # If no good break points, just split at max length
        else:
            while len(line) > max_length:
                # Find the last space before max_length
                break_point = line.rfind(" ", 0, max_length)
                if break_point == -1:
                    break_point = max_length

                fixed_lines.append(line[:break_point])
                line = line[break_point:].lstrip()

            if line:
                fixed_lines.append(line)

    return "\n".join(fixed_lines)
