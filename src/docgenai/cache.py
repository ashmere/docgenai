"""
Caching utilities for DocGenAI to improve performance.

This module provides caching for both generation results and model instances
to avoid expensive recomputation and reloading.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class CacheManager:
    """
    Unified cache manager for DocGenAI.

    Handles caching of generation results to avoid re-generating
    documentation for the same content and configuration.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize cache manager with configuration.

        Args:
            config: Cache configuration dictionary
        """
        self.enabled = config.get("enabled", True)
        self.cache_dir = Path(config.get("directory", ".docgenai_cache"))
        self.max_size_mb = config.get("max_size_mb", 1000)
        self.ttl_hours = config.get("ttl_hours", 24)

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.metadata_file = self.cache_dir / "metadata.json"
            self.metadata = self._load_metadata()
        else:
            self.metadata = {"entries": {}, "total_size_mb": 0}

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata (access times, sizes, etc.)"""
        if not self.enabled or not self.metadata_file.exists():
            return {"entries": {}, "total_size_mb": 0}

        try:
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"entries": {}, "total_size_mb": 0}

    def _save_metadata(self):
        """Save cache metadata to disk"""
        if not self.enabled:
            return

        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except IOError:
            pass  # Fail silently if we can't save metadata

    def get_cache_key(self, file_path: str, include_architecture: bool = True) -> str:
        """
        Generate cache key from file content and options.

        Args:
            file_path: Path to the source file
            include_architecture: Whether architecture analysis is included

        Returns:
            Cache key string
        """
        try:
            # Read file content
            with open(file_path, "rb") as f:
                content = f.read()

            # Get file modification time
            mtime = Path(file_path).stat().st_mtime

            # Create cache key from content hash, mtime, and options
            content_hash = hashlib.md5(content).hexdigest()
            options_str = f"arch_{include_architecture}"
            cache_key = f"{content_hash}_{int(mtime)}_{options_str}"

            return cache_key

        except (IOError, OSError):
            # If we can't read the file, generate a unique key
            return f"error_{file_path}_{int(time.time())}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache entry"""
        return self.cache_dir / f"{cache_key}.json"

    def _is_expired(self, entry_info: Dict[str, Any]) -> bool:
        """Check if a cache entry is expired"""
        created_time = entry_info.get("created", 0)
        current_time = time.time()
        age_hours = (current_time - created_time) / 3600
        return age_hours > self.ttl_hours

    def _cleanup_cache(self):
        """Remove old cache entries if cache size exceeds limit"""
        if not self.enabled or self.metadata["total_size_mb"] <= self.max_size_mb:
            return

        entries = self.metadata["entries"]

        # Remove expired entries first
        expired_keys = []
        for cache_key, entry_info in entries.items():
            if self._is_expired(entry_info):
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            self._remove_cache_entry(cache_key)

        # If still over limit, remove oldest entries
        if self.metadata["total_size_mb"] > self.max_size_mb:
            sorted_entries = sorted(
                entries.items(), key=lambda x: x[1].get("last_access", 0)
            )

            target_size = self.max_size_mb * 0.8  # Keep 20% buffer
            for cache_key, entry_info in sorted_entries:
                if self.metadata["total_size_mb"] <= target_size:
                    break
                self._remove_cache_entry(cache_key)

        self._save_metadata()

    def _remove_cache_entry(self, cache_key: str):
        """Remove a single cache entry"""
        cache_file = self._get_cache_path(cache_key)
        if cache_file.exists():
            cache_file.unlink()

        if cache_key in self.metadata["entries"]:
            entry_info = self.metadata["entries"][cache_key]
            self.metadata["total_size_mb"] -= entry_info.get("size_mb", 0)
            del self.metadata["entries"][cache_key]

    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached generation result.

        Args:
            cache_key: Cache key from get_cache_key()

        Returns:
            Cached result dictionary if found, None otherwise
        """
        if not self.enabled:
            return None

        cache_file = self._get_cache_path(cache_key)
        if not cache_file.exists():
            return None

        # Check if entry exists in metadata
        if cache_key not in self.metadata["entries"]:
            return None

        # Check if expired
        entry_info = self.metadata["entries"][cache_key]
        if self._is_expired(entry_info):
            self._remove_cache_entry(cache_key)
            return None

        try:
            # Update access time
            self.metadata["entries"][cache_key]["last_access"] = time.time()
            self._save_metadata()

            # Return cached content
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

        except (IOError, json.JSONDecodeError, UnicodeDecodeError):
            # Cache file corrupted, remove it
            self._remove_cache_entry(cache_key)
            return None

    def cache_result(self, cache_key: str, result: Dict[str, Any]):
        """
        Cache a generation result.

        Args:
            cache_key: Cache key from get_cache_key()
            result: Generation result dictionary to cache
        """
        if not self.enabled:
            return

        cache_file = self._get_cache_path(cache_key)

        try:
            # Prepare result for caching (remove non-serializable items)
            cacheable_result = {
                "input_file": result.get("input_file"),
                "output_file": result.get("output_file"),
                "documentation": result.get("documentation"),
                "architecture_description": result.get("architecture_description"),
                "generation_time": result.get("generation_time"),
                "cached_at": time.time(),
            }

            # Write cache file
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cacheable_result, f, indent=2)

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
            }

            self._save_metadata()

            # Cleanup if needed
            self._cleanup_cache()

        except (IOError, json.JSONEncodeError):
            pass  # Fail silently if we can't cache

    def clear_cache(self):
        """Clear all cache entries"""
        if not self.enabled:
            return

        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

        # Reset metadata
        self.metadata = {"entries": {}, "total_size_mb": 0}
        self._save_metadata()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "enabled": self.enabled,
            "total_entries": len(self.metadata["entries"]),
            "cache_size_mb": round(self.metadata["total_size_mb"], 2),
            "cache_dir": str(self.cache_dir),
            "max_size_mb": self.max_size_mb,
            "ttl_hours": self.ttl_hours,
        }


# Backward compatibility
class GenerationCache(CacheManager):
    """Backward compatibility wrapper for GenerationCache."""

    def __init__(self, cache_dir: Path, max_size_mb: int = 1000):
        config = {
            "enabled": True,
            "directory": str(cache_dir),
            "max_size_mb": max_size_mb,
            "ttl_hours": 24,
        }
        super().__init__(config)

    def get(self, content: str, prompt_type: str = "default") -> Optional[str]:
        """Legacy method for getting cached content."""
        # Generate a simple cache key from content
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cache_key = f"{content_hash}_{prompt_type}"

        result = self.get_cached_result(cache_key)
        if result:
            return result.get("documentation", "")
        return None

    def set(self, content: str, result: str, prompt_type: str = "default"):
        """Legacy method for setting cached content."""
        # Generate a simple cache key from content
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cache_key = f"{content_hash}_{prompt_type}"

        # Create result dictionary
        result_dict = {"documentation": result, "generation_time": 0}

        self.cache_result(cache_key, result_dict)

    def clear(self):
        """Legacy method for clearing cache."""
        self.clear_cache()


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
