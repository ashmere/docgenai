"""
Intelligent Chunker for DocGenAI

This module implements smart chunking of files for LLM consumption, respecting
token limits and extracting key signatures from large files.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class FileChunk:
    """Represents a chunk of files for LLM processing."""

    files: List[Path]
    content: str
    estimated_tokens: int
    chunk_id: int
    is_signature_only: bool = False


class Chunker:
    """Chunk files intelligently for LLM consumption with token awareness."""

    def __init__(self, config: Dict, model=None):
        """Initialize the chunker with configuration and optional model."""
        self.config = config
        self.model = model
        self.chunking_config = config.get("chunking", {})

        # Get token limits from model or config
        if model and hasattr(model, "get_context_limit"):
            self.max_context_tokens = model.get_context_limit()
        else:
            self.max_context_tokens = self.chunking_config.get(
                "max_context_tokens", 16384
            )

        # Use safety margin (75% of context limit)
        safety_margin = self.chunking_config.get("safety_margin", 0.75)
        self.max_chunk_tokens = int(self.max_context_tokens * safety_margin)

        self.overlap_tokens = self.chunking_config.get("overlap_tokens", 500)
        self.prefer_file_boundaries = self.chunking_config.get(
            "prefer_file_boundaries", True
        )

        # Signature extraction threshold (chars)
        self.signature_threshold = self.chunking_config.get("signature_threshold", 5000)

        logger.info(f"🔧 Chunker initialized: " f"max_tokens={self.max_chunk_tokens}")

    def chunk_files(self, files: List[Path]) -> List[FileChunk]:
        """
        Chunk files intelligently for LLM consumption.

        Args:
            files: List of file paths to chunk

        Returns:
            List of FileChunk objects ready for LLM processing
        """
        logger.info(f"📦 Chunking {len(files)} files for LLM processing")

        chunks = []
        current_chunk_files = []
        current_chunk_content = []
        current_tokens = 0
        chunk_id = 0

        for file_path in files:
            try:
                file_content = self._read_file_smart(file_path)
                file_tokens = self._estimate_tokens(file_content)

                # Check if this file would exceed chunk limit
                if current_tokens + file_tokens > self.max_chunk_tokens:
                    # Save current chunk if it has content
                    if current_chunk_files:
                        chunks.append(
                            self._create_chunk(
                                current_chunk_files,
                                current_chunk_content,
                                current_tokens,
                                chunk_id,
                            )
                        )
                        chunk_id += 1

                    # Start new chunk
                    current_chunk_files = [file_path]
                    current_chunk_content = [file_content]
                    current_tokens = file_tokens

                    # If single file is too large, split it
                    if file_tokens > self.max_chunk_tokens:
                        large_file_chunks = self._split_large_file(file_path, chunk_id)
                        chunks.extend(large_file_chunks)
                        chunk_id += len(large_file_chunks)

                        # Reset for next files
                        current_chunk_files = []
                        current_chunk_content = []
                        current_tokens = 0
                else:
                    # Add to current chunk
                    current_chunk_files.append(file_path)
                    current_chunk_content.append(file_content)
                    current_tokens += file_tokens

            except Exception as e:
                logger.warning(f"⚠️ Error processing {file_path}: {e}")
                continue

        # Add final chunk if it has content
        if current_chunk_files:
            chunks.append(
                self._create_chunk(
                    current_chunk_files, current_chunk_content, current_tokens, chunk_id
                )
            )

        logger.info(f"✅ Created {len(chunks)} chunks")
        return chunks

    def _read_file_smart(self, file_path: Path) -> str:
        """Read file, extracting signatures if too large."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # If file is too large, extract signatures only
            if len(content) > self.signature_threshold:
                logger.debug(f"📝 Extracting signatures from {file_path.name}")
                return self._extract_signatures(content, file_path.suffix)

            return content

        except Exception as e:
            logger.warning(f"⚠️ Error reading {file_path}: {e}")
            return f"# Error reading file: {file_path}\n# {str(e)}"

    def _extract_signatures(self, content: str, file_extension: str) -> str:
        """Extract function/class signatures, imports, and structure."""
        lines = content.split("\n")
        important_lines = []

        # Language-specific patterns
        signature_patterns = self._get_signature_patterns(file_extension)

        in_multiline_comment = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Handle multiline comments
            if "/*" in stripped and "*/" not in stripped:
                in_multiline_comment = True
            elif "*/" in stripped:
                in_multiline_comment = False
                continue
            elif in_multiline_comment:
                continue

            # Keep important lines
            should_keep = False

            # Empty lines for structure
            if len(stripped) == 0:
                should_keep = True

            # Comments (single line)
            elif any(
                stripped.startswith(comment)
                for comment in ["#", "//", "/*", "*", "<!--", "--"]
            ):
                should_keep = True

            # Imports and includes
            elif any(
                stripped.startswith(imp)
                for imp in [
                    "import ",
                    "from ",
                    "include ",
                    "#include",
                    "require(",
                    "const ",
                    "let ",
                    "var ",
                    "export ",
                    "package ",
                ]
            ):
                should_keep = True

            # Function/class/interface signatures
            elif any(pattern in stripped for pattern in signature_patterns):
                should_keep = True
                # Include next few lines for context
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith("}"):
                        important_lines.append(lines[j])

            # Structural elements
            elif any(char in stripped for char in ["{", "}", "(", ")"]):
                should_keep = True

            # Type definitions and interfaces
            elif any(
                stripped.startswith(typedef)
                for typedef in ["type ", "interface ", "struct ", "enum ", "class "]
            ):
                should_keep = True

            if should_keep:
                important_lines.append(line)

        # Add summary header
        original_lines = len(lines)
        extracted_lines = len(important_lines)
        header = f"""# SIGNATURE EXTRACTION SUMMARY
# Original file: {original_lines} lines
# Extracted: {extracted_lines} lines ({extracted_lines/original_lines*100:.1f}%)
# Contains: imports, signatures, structure, comments

"""

        return header + "\n".join(important_lines)

    def _get_signature_patterns(self, file_extension: str) -> List[str]:
        """Get signature patterns based on file extension."""
        patterns = {
            ".py": ["def ", "class ", "async def ", "@"],
            ".js": ["function ", "const ", "let ", "var ", "class ", "=>"],
            ".ts": [
                "function ",
                "const ",
                "let ",
                "var ",
                "class ",
                "interface ",
                "type ",
                "=>",
                "export ",
                "import ",
            ],
            ".tsx": [
                "function ",
                "const ",
                "let ",
                "var ",
                "class ",
                "interface ",
                "type ",
                "=>",
                "export ",
                "import ",
            ],
            ".jsx": ["function ", "const ", "let ", "var ", "class ", "=>"],
            ".go": ["func ", "type ", "var ", "const ", "import ", "package "],
            ".java": [
                "public ",
                "private ",
                "protected ",
                "class ",
                "interface ",
                "enum ",
                "import ",
                "package ",
            ],
            ".cpp": [
                "class ",
                "struct ",
                "enum ",
                "namespace ",
                "template ",
                "public:",
                "private:",
                "protected:",
                "#include",
            ],
            ".c": ["struct ", "enum ", "typedef ", "#include", "#define"],
            ".h": ["struct ", "enum ", "typedef ", "#include", "#define"],
            ".rs": [
                "fn ",
                "struct ",
                "enum ",
                "impl ",
                "trait ",
                "use ",
                "mod ",
                "pub ",
            ],
            ".rb": ["def ", "class ", "module ", "include ", "require"],
            ".php": [
                "function ",
                "class ",
                "interface ",
                "trait ",
                "use ",
                "namespace ",
                "public ",
                "private ",
                "protected",
            ],
        }

        return patterns.get(
            file_extension.lower(),
            ["function ", "class ", "def ", "public ", "private"],
        )

    def _estimate_tokens(self, content: str) -> int:
        """Estimate token count for content."""
        if self.model and hasattr(self.model, "estimate_tokens"):
            return self.model.estimate_tokens(content)

        # Fallback estimation (roughly 3.2 chars per token)
        return len(content) // 3

    def _create_chunk(
        self, files: List[Path], contents: List[str], tokens: int, chunk_id: int
    ) -> FileChunk:
        """Create a FileChunk from files and content."""
        # Combine content with file headers
        chunk_content = ""

        for file_path, content in zip(files, contents):
            chunk_content += f"\n# FILE: {file_path}\n"
            chunk_content += f"# Path: {file_path.absolute()}\n"
            chunk_content += f"# Size: {len(content)} chars\n"
            chunk_content += "# " + "=" * 50 + "\n\n"
            chunk_content += content
            chunk_content += "\n\n"

        return FileChunk(
            files=files,
            content=chunk_content,
            estimated_tokens=tokens,
            chunk_id=chunk_id,
            is_signature_only=any(
                "SIGNATURE EXTRACTION" in content for content in contents
            ),
        )

    def _split_large_file(
        self, file_path: Path, start_chunk_id: int
    ) -> List[FileChunk]:
        """Split a large file into multiple chunks."""
        logger.info(f"🔪 Splitting large file: {file_path.name}")

        try:
            # For very large files, use signature extraction
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            signature_content = self._extract_signatures(content, file_path.suffix)

            # If signature extraction is still too large, split by sections
            if self._estimate_tokens(signature_content) > self.max_chunk_tokens:
                return self._split_by_sections(
                    file_path, signature_content, start_chunk_id
                )

            # Single signature chunk
            return [
                FileChunk(
                    files=[file_path],
                    content=f"\n# FILE: {file_path}\n"
                    f"# Path: {file_path.absolute()}\n"
                    f"# Large file - signature extraction\n"
                    f"# " + "=" * 50 + "\n\n"
                    f"{signature_content}",
                    estimated_tokens=self._estimate_tokens(signature_content),
                    chunk_id=start_chunk_id,
                    is_signature_only=True,
                )
            ]

        except Exception as e:
            logger.error(f"❌ Error splitting file {file_path}: {e}")
            return []

    def _split_by_sections(
        self, file_path: Path, content: str, start_chunk_id: int
    ) -> List[FileChunk]:
        """Split content by logical sections."""
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = start_chunk_id

        for line in lines:
            line_tokens = self._estimate_tokens(line)

            if current_tokens + line_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunk_content = "\n".join(current_chunk)
                    chunks.append(
                        FileChunk(
                            files=[file_path],
                            content=f"\n# FILE: {file_path} (part {chunk_id - start_chunk_id + 1})\n"
                            f"# Path: {file_path.absolute()}\n"
                            f"# Section of large file\n"
                            f"# " + "=" * 50 + "\n\n"
                            f"{chunk_content}",
                            estimated_tokens=current_tokens,
                            chunk_id=chunk_id,
                            is_signature_only=True,
                        )
                    )
                    chunk_id += 1

                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens

        # Add final chunk
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            chunks.append(
                FileChunk(
                    files=[file_path],
                    content=f"\n# FILE: {file_path} (part {chunk_id - start_chunk_id + 1})\n"
                    f"# Path: {file_path.absolute()}\n"
                    f"# Section of large file\n"
                    f"# " + "=" * 50 + "\n\n"
                    f"{chunk_content}",
                    estimated_tokens=current_tokens,
                    chunk_id=chunk_id,
                    is_signature_only=True,
                )
            )

        logger.info(f"📦 Split into {len(chunks)} sections")
        return chunks
