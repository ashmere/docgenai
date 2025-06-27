"""
Caching utilities for DocGenAI to improve performance.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class GenerationCache:
    """
    Handles caching of generation results to avoid re-generating
    documentation for the same content.
    """

    def __init__(self, cache_dir: Path, max_size_mb: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache metadata file
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata (access times, sizes, etc.)"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"entries": {}, "total_size_mb": 0}

    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except IOError:
            pass  # Fail silently if we can't save metadata

    def _get_content_hash(self, content: str, prompt_type: str) -> str:
        """Generate a hash for the content and prompt type"""
        combined = f"{prompt_type}:{content}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache entry"""
        return self.cache_dir / f"{cache_key}.txt"

    def _cleanup_cache(self):
        """Remove old cache entries if cache size exceeds limit"""
        if self.metadata["total_size_mb"] <= self.max_size_mb:
            return

        # Sort entries by last access time (oldest first)
        entries = self.metadata["entries"]
        sorted_entries = sorted(
            entries.items(), key=lambda x: x[1].get("last_access", 0)
        )

        # Remove oldest entries until under size limit
        for cache_key, entry_info in sorted_entries:
            if self.metadata["total_size_mb"] <= self.max_size_mb * 0.8:
                break  # Keep 20% buffer

            cache_file = self._get_cache_path(cache_key)
            if cache_file.exists():
                cache_file.unlink()

            # Update metadata
            self.metadata["total_size_mb"] -= entry_info.get("size_mb", 0)
            del self.metadata["entries"][cache_key]

        self._save_metadata()

    def get(self, content: str, prompt_type: str = "default") -> Optional[str]:
        """
        Get cached generation result for the given content.

        Args:
            content: The source content (code, etc.)
            prompt_type: Type of prompt/generation (e.g., "analyze", "docs", "diagram")

        Returns:
            Cached result if found, None otherwise
        """
        cache_key = self._get_content_hash(content, prompt_type)
        cache_file = self._get_cache_path(cache_key)

        if not cache_file.exists():
            return None

        try:
            # Update access time
            if cache_key in self.metadata["entries"]:
                self.metadata["entries"][cache_key]["last_access"] = time.time()
                self._save_metadata()

            # Return cached content
            return cache_file.read_text(encoding="utf-8")

        except (IOError, UnicodeDecodeError):
            # Cache file corrupted, remove it
            if cache_file.exists():
                cache_file.unlink()
            if cache_key in self.metadata["entries"]:
                del self.metadata["entries"][cache_key]
            return None

    def set(self, content: str, result: str, prompt_type: str = "default"):
        """
        Cache a generation result.

        Args:
            content: The source content (code, etc.)
            result: The generated result to cache
            prompt_type: Type of prompt/generation
        """
        cache_key = self._get_content_hash(content, prompt_type)
        cache_file = self._get_cache_path(cache_key)

        try:
            # Write cache file
            cache_file.write_text(result, encoding="utf-8")

            # Calculate file size
            file_size_mb = cache_file.stat().st_size / (1024 * 1024)

            # Update metadata
            current_time = time.time()
            if cache_key in self.metadata["entries"]:
                # Update existing entry
                old_size = self.metadata["entries"][cache_key].get("size_mb", 0)
                self.metadata["total_size_mb"] += file_size_mb - old_size
            else:
                # New entry
                self.metadata["total_size_mb"] += file_size_mb

            self.metadata["entries"][cache_key] = {
                "created": current_time,
                "last_access": current_time,
                "size_mb": file_size_mb,
                "prompt_type": prompt_type,
            }

            self._save_metadata()

            # Cleanup if needed
            self._cleanup_cache()

        except IOError:
            pass  # Fail silently if we can't cache

    def clear(self):
        """Clear all cache entries"""
        for cache_file in self.cache_dir.glob("*.txt"):
            cache_file.unlink()

        self.metadata = {"entries": {}, "total_size_mb": 0}
        self._save_metadata()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.metadata["entries"]),
            "total_size_mb": round(self.metadata["total_size_mb"], 2),
            "cache_dir": str(self.cache_dir),
            "max_size_mb": self.max_size_mb,
        }


class ModelCache:
    """
    Handles session-level model caching to avoid reloading models.
    """

    def __init__(self):
        self._cached_model = None
        self._cached_model_name = None
        self._cached_config = None

    def get_model(self, model_name: str, config: Any):
        """
        Get cached model if it matches the requested configuration.

        Returns:
            Cached model if available and matches, None otherwise
        """
        if (
            self._cached_model is not None
            and self._cached_model_name == model_name
            and self._cached_config == config
        ):
            return self._cached_model
        return None

    def set_model(self, model_name: str, model: Any, config: Any):
        """Cache a model for the session"""
        self._cached_model = model
        self._cached_model_name = model_name
        self._cached_config = config

    def clear(self):
        """Clear the cached model"""
        self._cached_model = None
        self._cached_model_name = None
        self._cached_config = None
