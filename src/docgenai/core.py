"""
Core Documentation Generator for DocGenAI

This module implements smart file selection, intelligent chunking, and
high-quality prompts to generate excellent technical documentation.
"""

import logging
import platform
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache import CacheManager
from .chunker import Chunker, FileChunk
from .file_selector import FileSelector
from .models import AIModel
from .prompts import ARCHITECTURE_ANALYSIS_PROMPT, MULTI_CHUNK_SYNTHESIS_PROMPT
from .prompts.architecture import COMPREHENSIVE_ARCHITECTURE_PROMPT
from .prompts.refinement import create_refinement_chain
from .templates import TemplateManager

logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """
    Documentation generator using smart file selection,
    intelligent chunking, and high-quality prompts.
    """

    def __init__(self, model: AIModel, config: Dict[str, Any]):
        """Initialize the simplified documentation generator."""
        self.model = model
        self.config = config

        # Initialize components
        self.file_selector = FileSelector(config)
        self.chunker = Chunker(config, model)
        self.cache_manager = CacheManager(config.get("cache", {}))
        self.template_manager = TemplateManager(config.get("templates", {}))

        # Configuration
        self.chains_config = config.get("chains", {})
        self.output_config = config.get("output", {})

        logger.info("🚀 DocumentationGenerator initialized")
        logger.info(f"📋 Model: {model.get_model_info()['model_path']}")
        logger.info(f"🔧 Max tokens: {self.chunker.max_chunk_tokens}")

    def generate_documentation(
        self, codebase_path: Path, output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate documentation for a codebase using the simplified approach.

        Args:
            codebase_path: Path to the codebase to analyze
            output_dir: Directory to save generated documentation

        Returns:
            Dictionary with generation results and metadata
        """
        logger.info(f"📖 Generating documentation for: {codebase_path}")
        start_time = time.time()

        try:
            # Phase 1: File Selection
            logger.info("🔍 Phase 1: File selection")
            selected_files = self.file_selector.select_important_files(codebase_path)

            if not selected_files:
                logger.error("❌ No files selected for analysis")
                return {"success": False, "error": "No files found"}

            # Phase 2: Chunking
            logger.info("📦 Phase 2: Chunking")
            chunks = self.chunker.chunk_files(selected_files)

            if not chunks:
                logger.error("❌ No chunks created")
                return {"success": False, "error": "Chunking failed"}

            # Store metadata for potential separate file saving
            self._current_files = selected_files
            self._current_chunks = chunks

            # Phase 3: Documentation Generation
            logger.info("📝 Phase 3: Documentation generation")
            if len(chunks) == 1:
                # Single chunk - direct analysis
                documentation = self._analyze_single_chunk(chunks[0])
            else:
                # Multiple chunks - analyze then synthesize
                documentation = self._analyze_multiple_chunks(chunks)

            # Phase 4: Optional Refinement
            if self.chains_config.get("enable_refinement", False):
                logger.info("✨ Phase 4: Documentation refinement")
                documentation = self._refine_documentation(documentation)

            # Phase 5: Save Results
            output_path = self._save_documentation(
                codebase_path, documentation, output_dir
            )

            elapsed_time = time.time() - start_time
            logger.info(f"✅ Documentation generated in {elapsed_time:.2f}s")

            return {
                "success": True,
                "output_path": output_path,
                "files_analyzed": len(selected_files),
                "chunks_created": len(chunks),
                "generation_time": elapsed_time,
                "documentation": documentation,
            }

        except Exception as e:
            logger.error(f"❌ Documentation generation failed: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_single_chunk(self, chunk: FileChunk) -> str:
        """Analyze a single chunk of files."""
        logger.info(f"📝 Analyzing chunk with {len(chunk.files)} files")

        # Select architecture prompt based on configuration
        architecture_type = self.config.get("output", {}).get(
            "architecture_type", "standard"
        )
        if architecture_type == "comprehensive":
            prompt = COMPREHENSIVE_ARCHITECTURE_PROMPT.format(
                file_contents=chunk.content
            )
        else:
            prompt = ARCHITECTURE_ANALYSIS_PROMPT.format(file_contents=chunk.content)

        # Generate documentation
        documentation = self.model.generate_raw_response(prompt)

        # Clean up Mermaid formatting issues
        documentation = self._clean_mermaid_formatting(documentation)

        # Handle metadata based on configuration
        metadata_mode = self.output_config.get("metadata_mode", "footer")

        if metadata_mode == "none":
            return documentation
        elif metadata_mode == "footer":
            metadata = self._create_metadata(chunk.files, [chunk])
            return f"{documentation}\n\n{metadata}"
        elif metadata_mode == "file":
            # Metadata will be saved as separate file in _save_documentation
            return documentation
        else:
            # Default to footer for unknown modes
            metadata = self._create_metadata(chunk.files, [chunk])
            return f"{documentation}\n\n{metadata}"

    def _analyze_multiple_chunks(self, chunks: List[FileChunk]) -> str:
        """Analyze multiple chunks and synthesize results."""
        logger.info(f"📝 Analyzing {len(chunks)} chunks")

        # Analyze each chunk individually
        chunk_analyses = []
        for i, chunk in enumerate(chunks):
            logger.info(f"📝 Analyzing chunk {i+1}/{len(chunks)}")

            # Select architecture prompt based on configuration
            architecture_type = self.config.get("output", {}).get(
                "architecture_type", "standard"
            )
            if architecture_type == "comprehensive":
                prompt = COMPREHENSIVE_ARCHITECTURE_PROMPT.format(
                    file_contents=chunk.content
                )
            else:
                prompt = ARCHITECTURE_ANALYSIS_PROMPT.format(
                    file_contents=chunk.content
                )

            analysis = self.model.generate_raw_response(prompt)
            chunk_analyses.append(f"## CHUNK {i+1} ANALYSIS\n\n{analysis}")

        # Synthesize all analyses
        logger.info("🔄 Synthesizing chunk analyses")
        synthesis_prompt = MULTI_CHUNK_SYNTHESIS_PROMPT.format(
            chunk_analyses="\n\n".join(chunk_analyses)
        )

        documentation = self.model.generate_raw_response(synthesis_prompt)

        # Clean up Mermaid formatting issues
        documentation = self._clean_mermaid_formatting(documentation)

        # Handle metadata based on configuration
        metadata_mode = self.output_config.get("metadata_mode", "footer")

        if metadata_mode == "none":
            return documentation
        elif metadata_mode == "footer":
            all_files = []
            for chunk in chunks:
                all_files.extend(chunk.files)
            metadata = self._create_metadata(all_files, chunks)
            return f"{documentation}\n\n{metadata}"
        elif metadata_mode == "file":
            # Metadata will be saved as separate file in _save_documentation
            return documentation
        else:
            # Default to footer for unknown modes
            all_files = []
            for chunk in chunks:
                all_files.extend(chunk.files)
            metadata = self._create_metadata(all_files, chunks)
            return f"{documentation}\n\n{metadata}"

    def _refine_documentation(self, documentation: str) -> str:
        """Refine documentation using the refinement chain."""
        logger.info("✨ Refining documentation")

        try:
            refinement_chain = create_refinement_chain()

            # Execute refinement chain
            context = {"base_documentation": documentation}
            result = refinement_chain.execute(context, self.model)

            return result.get("final_documentation", documentation)

        except Exception as e:
            logger.warning(f"⚠️ Refinement failed, using original: {e}")
            return documentation

    def _clean_mermaid_formatting(self, documentation: str) -> str:
        """Clean up Mermaid diagram formatting issues."""
        # Check if we have the problematic pattern
        if "```text" in documentation:
            logger.info("🐛 Found ```text in documentation, cleaning...")
            # Count occurrences for debugging
            text_count = documentation.count("```text")
            logger.info(f"🔍 Found {text_count} instances of ```text")

        # Enhanced approach: remove ```text lines and following empty lines
        # This handles the common pattern of ```text followed by empty line
        lines = documentation.split("\n")
        cleaned_lines = []
        removed_count = 0
        skip_next_empty = False

        for i, line in enumerate(lines):
            # Skip lines that are exactly ```text (with optional whitespace)
            if line.strip() == "```text":
                logger.debug(f"🗑️ Removing line {i}: {repr(line)}")
                removed_count += 1
                skip_next_empty = True  # Skip the next empty line if present
                continue

            # Skip the empty line that follows ```text
            if skip_next_empty and line.strip() == "":
                logger.debug(f"🗑️ Removing empty line {i} after ```text")
                skip_next_empty = False
                continue

            skip_next_empty = False
            cleaned_lines.append(line)

        cleaned = "\n".join(cleaned_lines)
        logger.info(f"🧹 Removed {removed_count} ```text lines")

        # Check if cleaning worked
        if "```text" in cleaned:
            remaining_count = cleaned.count("```text")
            logger.warning(
                f"⚠️ Still found {remaining_count} ```text instances after cleaning!"
            )

            # Debug: Show context around remaining ```text
            remaining_lines = cleaned.split("\n")
            for i, line in enumerate(remaining_lines):
                if "```text" in line:
                    start = max(0, i - 2)
                    end = min(len(remaining_lines), i + 3)
                    logger.warning(f"📍 Context around line {i}:")
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        logger.warning(f"{marker}{j}: {repr(remaining_lines[j])}")
        else:
            logger.info("✅ Successfully cleaned ```text patterns")

        return cleaned

    def _create_metadata(self, files: List[Path], chunks: List[FileChunk]) -> str:
        """Create metadata section for the documentation."""
        file_tree = self._create_file_tree(files)

        signature_files = [chunk for chunk in chunks if chunk.is_signature_only]

        metadata = f"""---

## GENERATION METADATA

### Files Analyzed
- **Total files**: {len(files)}
- **Chunks created**: {len(chunks)}
- **Signature-only files**: {len(signature_files)}

### File Tree
```
{file_tree}
```

### Analysis Details
- **Generation time**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Model**: {self.model.get_model_info()['model_path']}
- **Max tokens per chunk**: {self.chunker.max_chunk_tokens}
- **Chunking strategy**: Token-aware with file boundaries

### Files Processed
{self._format_file_list(files)}

### Large Files (Signature Extraction)
{self._format_signature_files(signature_files)}

---

*Generated by DocGenAI using {self.model.get_model_info()['backend']} backend on {platform.system()}*"""
        return metadata

    def _create_file_tree(self, files: List[Path]) -> str:
        """Create a simple file tree representation."""
        if not files:
            return "No files"

        # Get common root
        common_root = Path(files[0]).parent
        for file_path in files[1:]:
            try:
                common_root = Path(
                    *common_root.parts[: len(Path(file_path).parent.parts)]
                )
            except (ValueError, IndexError):
                continue

        # Create tree
        tree_lines = []
        for file_path in sorted(files):
            try:
                rel_path = file_path.relative_to(common_root)
                tree_lines.append(f"  {rel_path}")
            except ValueError:
                tree_lines.append(f"  {file_path.name}")

        return "\n".join(tree_lines[:20])  # Limit to 20 files

    def _format_file_list(self, files: List[Path]) -> str:
        """Format the list of processed files."""
        lines = []
        for file_path in sorted(files)[:20]:  # Limit to 20 files
            size = file_path.stat().st_size if file_path.exists() else 0
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f}KB"
            lines.append(f"- `{file_path.name}` ({size_str})")

        if len(files) > 20:
            lines.append(f"- ... and {len(files) - 20} more files")

        return "\n".join(lines)

    def _format_signature_files(self, signature_chunks: List[FileChunk]) -> str:
        """Format information about files that used signature extraction."""
        if not signature_chunks:
            return "None - all files processed in full"

        lines = []
        for chunk in signature_chunks:
            for file_path in chunk.files:
                lines.append(f"- `{file_path.name}` (signature extraction)")

        return "\n".join(lines)

    def _save_documentation(
        self, codebase_path: Path, documentation: str, output_dir: Path
    ) -> Path:
        """Save the generated documentation to a file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create output filename
        project_name = codebase_path.name
        output_filename = f"{project_name}_documentation.md"
        output_path = output_dir / output_filename

        # Use template if configured
        if self.template_manager:
            try:
                context = {
                    "project_name": project_name,
                    "documentation": documentation,
                    "generation_date": time.strftime("%Y-%m-%d"),
                    "codebase_path": str(codebase_path),
                    "config": self.config,
                    "model_info": self.model.get_model_info(),
                }
                rendered_doc = self.template_manager.render_documentation(context)
                documentation = rendered_doc
            except Exception as e:
                logger.warning(f"⚠️ Template rendering failed: {e}")

        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(documentation)

        # Handle metadata file mode
        metadata_mode = self.output_config.get("metadata_mode", "footer")
        if metadata_mode == "file" and hasattr(self, "_current_files"):
            metadata_filename = f"{project_name}_documentation.metadata.md"
            metadata_path = output_dir / metadata_filename
            metadata_content = self._create_metadata(
                self._current_files, self._current_chunks
            )

            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write(metadata_content)

            logger.info(f"📊 Metadata saved to: {metadata_path}")

        logger.info(f"💾 Documentation saved to: {output_path}")
        return output_path


def generate_documentation(
    codebase_path: str,
    output_dir: str = "output",
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate documentation for a codebase.

    Args:
        codebase_path: Path to codebase to analyze
        output_dir: Output directory for documentation
        config: Optional configuration override

    Returns:
        Generation results and metadata
    """
    from .config import load_config
    from .models import create_model

    # Load configuration
    if config is None:
        config = load_config()

    # Create model
    model = create_model(config)

    # Create generator
    generator = DocumentationGenerator(model, config)

    # Generate documentation
    return generator.generate_documentation(Path(codebase_path), Path(output_dir))
