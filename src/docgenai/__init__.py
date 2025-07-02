"""
DocGenAI: AI-powered code documentation generator.

Uses DeepSeek-Coder models with platform-specific optimization for
generating comprehensive code documentation with multi-file analysis,
prompt chaining, and customizable templates.
"""

from pathlib import Path

import toml


def get_version():
    """Get version from pyproject.toml."""
    try:
        # Look for pyproject.toml in the package root or parent directories
        current = Path(__file__).parent
        for _ in range(3):  # Check up to 3 levels up
            pyproject_path = current / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    pyproject_data = toml.load(f)
                    return (
                        pyproject_data.get("tool", {})
                        .get("poetry", {})
                        .get("version", "unknown")
                    )
            current = current.parent
        return "unknown"
    except Exception:
        return "unknown"


__version__ = get_version()

__all__ = ["__version__"]
