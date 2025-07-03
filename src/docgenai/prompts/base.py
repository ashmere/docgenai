"""
Base Prompt Templates for DocGenAI

Common prompt templates and utilities used across different prompt types.
"""

BASE_PROMPT_TEMPLATES = {
    "file_header": """
# FILE: {file_path}
# Path: {absolute_path}
# Size: {file_size} chars
# Language: {language}
# ============================================================

""",
    "chunk_header": """
# CHUNK {chunk_id} of {total_chunks}
# Files: {file_count}
# Estimated tokens: {token_count}
# Contains: {file_list}
# ============================================================

""",
    "analysis_footer": """

---

**Analysis Guidelines:**
- Focus on practical insights for developers and systems engineers
- Be specific about file names, class names, and code structure
- Explain architectural decisions and trade-offs
- Highlight important patterns and conventions
- Point out potential areas for improvement
- Use clear, professional language
""",
    "synthesis_footer": """

---

**Synthesis Guidelines:**
- Integrate insights from all chunks coherently
- Resolve any conflicts or inconsistencies
- Maintain focus on architectural understanding
- Provide actionable guidance for developers
- Highlight system-wide patterns and relationships
""",
    "error_handling": """
# ERROR PROCESSING FILE: {file_path}
# Error: {error_message}
#
# This file could not be processed but may contain important information.
# Manual review recommended.
""",
    "large_file_notice": """
# LARGE FILE NOTICE: {file_path}
# Original size: {original_size} lines
# Extracted: {extracted_size} lines ({percentage}%)
#
# This file was too large for full analysis. Only key signatures,
# imports, and structural elements have been extracted.
""",
    "signature_extraction_header": """
# SIGNATURE EXTRACTION SUMMARY
# Original file: {original_lines} lines
# Extracted: {extracted_lines} lines ({percentage:.1f}%)
# Contains: imports, signatures, structure, comments
#
# This extraction preserves the most important structural elements
# while reducing size for LLM processing.

""",
}

PROMPT_FORMATTING_UTILS = {
    "format_file_list": lambda files: ", ".join(f.name for f in files),
    "format_file_size": lambda size: (
        f"{size:,} chars" if size < 1024 else f"{size/1024:.1f}KB"
    ),
    "format_token_count": lambda tokens: f"{tokens:,} tokens",
    "detect_language": lambda file_path: (
        file_path.suffix.lower().lstrip(".") or "text"
    ),
}


def format_file_header(file_path, content_size=None):
    """Format a standard file header for documentation."""
    return BASE_PROMPT_TEMPLATES["file_header"].format(
        file_path=file_path.name,
        absolute_path=file_path.absolute(),
        file_size=content_size or len(file_path.read_text(errors="ignore")),
        language=PROMPT_FORMATTING_UTILS["detect_language"](file_path),
    )


def format_chunk_header(chunk_id, total_chunks, files, token_count):
    """Format a standard chunk header for multi-chunk analysis."""
    return BASE_PROMPT_TEMPLATES["chunk_header"].format(
        chunk_id=chunk_id,
        total_chunks=total_chunks,
        file_count=len(files),
        token_count=PROMPT_FORMATTING_UTILS["format_token_count"](token_count),
        file_list=PROMPT_FORMATTING_UTILS["format_file_list"](files),
    )


def format_error_notice(file_path, error_message):
    """Format an error notice for files that couldn't be processed."""
    return BASE_PROMPT_TEMPLATES["error_handling"].format(
        file_path=file_path, error_message=str(error_message)
    )


def format_large_file_notice(file_path, original_size, extracted_size):
    """Format a notice for large files with signature extraction."""
    percentage = (extracted_size / original_size * 100) if original_size > 0 else 0
    return BASE_PROMPT_TEMPLATES["large_file_notice"].format(
        file_path=file_path,
        original_size=original_size,
        extracted_size=extracted_size,
        percentage=f"{percentage:.1f}%",
    )
