"""
Post-processing module for markdown linting and quality improvements.

This module handles systematic cleanup of generated documentation to ensure
it passes markdownlint checks and maintains high quality standards.
"""

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


def process_generated_markdown(content: str) -> str:
    """
    Apply comprehensive post-processing to generated markdown content.

    Args:
        content: Raw markdown content from AI generation

    Returns:
        Cleaned and lint-compliant markdown content
    """
    # Apply all post-processing steps in order
    content = fix_fenced_code_blocks(content)
    content = fix_list_spacing(content)
    content = fix_line_length(content)
    content = fix_heading_issues(content)
    content = fix_strong_style(content)
    content = remove_trailing_whitespace(content)
    content = fix_single_trailing_newline(content)
    # Fix blank lines last since other functions may add blank lines
    content = fix_multiple_blank_lines(content)

    return content


def fix_multiple_blank_lines(content: str) -> str:
    """
    Fix MD012: Multiple consecutive blank lines.

    Replaces multiple consecutive blank lines with single blank lines.
    This addresses the specific issue seen in test_output/multi_file_demo.md:8
    """
    # Split into lines and process
    lines = content.split("\n")
    result_lines = []
    consecutive_empty = 0

    for line in lines:
        if line.strip() == "":  # Empty or whitespace-only line
            consecutive_empty += 1
            if consecutive_empty <= 1:  # Allow one blank line
                result_lines.append("")
            # Skip additional blank lines
        else:
            consecutive_empty = 0
            result_lines.append(line)

    return "\n".join(result_lines)


def fix_fenced_code_blocks(content: str) -> str:
    """
    Fix MD031: Fenced code blocks should be surrounded by blank lines.

    Ensures proper spacing around code blocks for better readability.
    """
    lines = content.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a code block
        if line.strip().startswith("```"):
            # Ensure blank line before code block (unless it's the first line)
            if i > 0 and result_lines and result_lines[-1].strip() != "":
                result_lines.append("")

            # Add the opening code block line
            result_lines.append(line)
            i += 1

            # Find the closing ``` and add all content in between
            while i < len(lines):
                current_line = lines[i]
                result_lines.append(current_line)

                # If we found the closing ```, ensure blank line after
                if current_line.strip() == "```":
                    # Ensure blank line after code block (unless it's the last line)
                    if i + 1 < len(lines) and lines[i + 1].strip() != "":
                        result_lines.append("")
                    break
                i += 1
        else:
            result_lines.append(line)

        i += 1

    return "\n".join(result_lines)


def fix_list_spacing(content: str) -> str:
    """
    Fix MD032: Lists should be surrounded by blank lines.

    Ensures proper spacing around lists for better readability.
    """
    lines = content.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a list
        if line.strip() and (
            line.strip().startswith(("- ", "* ", "+ "))
            or re.match(r"^\s*\d+\.\s", line)
        ):
            # Ensure blank line before list (unless it's the first line)
            if i > 0 and result_lines and result_lines[-1].strip() != "":
                result_lines.append("")

            # Add the list item
            result_lines.append(line)
            j = i + 1

            # Look ahead to include all list items and indented content
            while j < len(lines):
                next_line = lines[j]

                # Continue if it's another list item, blank line, or indented content
                if (
                    next_line.strip() == ""
                    or next_line.strip().startswith(("- ", "* ", "+ "))
                    or re.match(r"^\s*\d+\.\s", next_line)
                    or (
                        next_line.startswith("  ") and next_line.strip()
                    )  # Indented content
                ):
                    result_lines.append(next_line)
                    j += 1
                else:
                    break

            # Ensure blank line after list
            if j < len(lines) and lines[j].strip() != "":
                result_lines.append("")

            i = j - 1  # -1 because we'll increment at the end of the loop
        else:
            result_lines.append(line)

        i += 1

    return "\n".join(result_lines)


def fix_line_length(content: str, max_length: int = 400) -> str:
    """
    Fix MD013: Line length violations.

    Breaks long lines at reasonable points while preserving markdown structure.
    """
    lines = content.split("\n")
    result_lines = []

    for line in lines:
        if len(line) <= max_length:
            result_lines.append(line)
            continue

        # Don't break certain types of lines
        if (
            line.strip().startswith("#")  # Headers
            or line.strip().startswith("```")  # Code blocks
            or line.strip().startswith("|")  # Tables
            or line.strip().startswith("[")  # Links
            or "](http" in line  # URLs
        ):
            result_lines.append(line)
            continue

        # Try to break at reasonable points
        if ", " in line:
            # Break at commas
            parts = line.split(", ")
            current_line = parts[0]

            for part in parts[1:]:
                if len(current_line + ", " + part) <= max_length:
                    current_line += ", " + part
                else:
                    result_lines.append(current_line + ",")
                    current_line = "  " + part  # Indent continuation

            result_lines.append(current_line)
        else:
            # Just break at max_length if no good break point
            result_lines.append(line)

    return "\n".join(result_lines)


def fix_heading_issues(content: str) -> str:
    """
    Fix MD024: Multiple headings with the same content and MD025: Multiple top level headings.

    This is complex to fix automatically, so we'll just log warnings for now.
    """
    lines = content.split("\n")
    headings = {}
    top_level_count = 0

    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            # Count heading level
            level = 0
            for char in line:
                if char == "#":
                    level += 1
                else:
                    break

            heading_text = line.strip("#").strip()

            if level == 1:
                top_level_count += 1

            if heading_text in headings:
                logger.warning(
                    f"MD024: Duplicate heading '{heading_text}' at line {i+1}"
                )
            else:
                headings[heading_text] = i + 1

    if top_level_count > 1:
        logger.warning(f"MD025: Multiple top level headings found ({top_level_count})")

    return content


def fix_strong_style(content: str) -> str:
    """
    Fix MD050: Strong style should use asterisks instead of underscores.

    Converts __text__ to **text** for consistency.
    """
    # Replace __text__ with **text**
    content = re.sub(r"__([^_]+)__", r"**\1**", content)
    return content


def fix_single_trailing_newline(content: str) -> str:
    """
    Fix MD047: Files should end with a single newline character.

    Ensures the file ends with exactly one newline.
    """
    # Remove all trailing whitespace and newlines, then add exactly one newline
    content = content.rstrip()
    content += "\n"
    return content


def remove_trailing_whitespace(content: str) -> str:
    """
    Remove trailing whitespace from all lines.
    """
    lines = content.split("\n")
    return "\n".join(line.rstrip() for line in lines)


def validate_markdown_quality(content: str) -> List[str]:
    """
    Validate markdown content and return list of remaining issues.

    Args:
        content: Markdown content to validate

    Returns:
        List of validation issues found
    """
    issues = []
    lines = content.split("\n")

    # Check for multiple blank lines
    for i in range(len(lines) - 2):
        if lines[i] == "" and lines[i + 1] == "" and lines[i + 2] == "":
            issues.append(f"MD012: Multiple blank lines at line {i + 1}")

    # Check for code block spacing
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            if i > 0 and lines[i - 1].strip() != "":
                issues.append(
                    f"MD031: Code block needs blank line before at line {i + 1}"
                )

            # Find closing ```
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "```":
                    if j + 1 < len(lines) and lines[j + 1].strip() != "":
                        issues.append(
                            f"MD031: Code block needs blank line after at line {j + 1}"
                        )
                    break

    return issues
