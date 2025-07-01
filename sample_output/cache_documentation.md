# Documentation: cache.py

## Overview

The `cache.py` module provides caching utilities for `DocGenAI` to improve performance by storing frequently used data, such as generation results and model instances, in memory or on disk. This helps in avoiding expensive recomputation and reloading operations, enhancing the efficiency of the application.

## Key Components

1. **CacheManager Class**:
   - **`**init**` Method**: Initializes the cache manager with configuration settings, including cache directory, maximum size, and time-to-live (TTL) hours.
   - **`_load_metadata` Method**: Loads cache metadata from a file.
   - **`_save_metadata` Method**: Saves cache metadata to a file.
   - **`get_cache_key` Method**: Generates a cache key from the file content and options.
   - **`_get_cache_path` Method**: Returns the file path for a cache entry.
   - **`_is_expired` Method**: Checks if a cache entry is expired.
   - **`_cleanup_cache` Method**: Removes old cache entries if the cache size exceeds the limit.
   - **`_remove_cache_entry` Method**: Removes a single cache entry.
   - **`get_cached_result` Method**: Retrieves a cached generation result.
   - **`cache_result` Method**: Caches a generation result.
   - **`clear_cache` Method**: Clears all cache entries.
   - **`get_stats` Method**: Gets cache statistics.

2. **GenerationCache Class**:
   - **`**init**` Method**: Initializes the `GenerationCache` with a cache directory and maximum size in megabytes.
   - **`get` Method**: Retrieves cached content based on the content hash and prompt type.
   - **`set` Method**: Sets cached content based on the content hash and prompt type.
   - **`clear` Method**: Clears the cache.

3. **ModelCache Class**:
   - **`**init**` Method**: Initializes the `ModelCache` with no attributes.
   - **`get_model` Method**: Retrieves a cached model if it matches the requested configuration.
   - **`set_model` Method**: Caches a model for the session.
   - **`clear` Method**: Clears the cached model.

## Architecture

The `CacheManager` class is the core of the caching system, handling both the storage and retrieval of cached data. The `GenerationCache` and `ModelCache` classes are backward compatibility wrappers around the `CacheManager` class, providing simplified interfaces for specific use cases.

## Usage Examples

Here's an example of how to use the `CacheManager` class to cache a generation result:

```python
config = {
    "enabled": True,
    "directory": ".docgenai_cache",
    "max_size_mb": 1000,
    "ttl_hours": 24,
}
cache_manager = CacheManager(config)

# Generate a cache key and result

cache_key = cache_manager.get_cache_key("path/to/source/file")
result = {"output_file": "path/to/output/file", "documentation": "cached documentation"}

# Cache the result

cache_manager.cache_result(cache_key, result)

# Retrieve the cached result

cached_result = cache_manager.get_cached_result(cache_key)
print(cached_result)

```

## Dependencies

- `hashlib`

- `json`

- `time`

- `pathlib`

- `typing`

## Configuration

- `enabled`: Enables or disables the cache.

- `directory`: Directory where cache files are stored.

- `max_size_mb`: Maximum size of the cache in megabytes.

- `ttl_hours`: Time-to-live for cached entries in hours.

## Error Handling

- Errors related to file operations (e.g., reading/writing files) are handled by the `try-except` blocks.

- If a file cannot be read or written, the operation is silently failed.

## Performance Considerations

- The cache is designed to be efficient by minimizing disk I/O and memory usage.

- The `_cleanup_cache` method ensures that the cache does not grow indefinitely by periodically removing old entries.

- The `get_cached_result` and `cache_result` methods are optimized to quickly check for and store cached data.

## Architecture Analysis

## Architectural Analysis of `src/docgenai/cache.py`

### 1. Architectural Patterns

The code primarily follows a **Singleton pattern** for the `CacheManager` class, ensuring that only one instance of the cache manager is used across the application. This is evident from the `**init**` method where it checks if an instance already exists and returns it if it does.

### 2. Code Organization

The code is organized into several components:

- **CacheManager**: Manages the cache for generation results and model instances.

- **GenerationCache**: A backward compatibility wrapper for `CacheManager`.

- **ModelCache**: Handles session-level model caching.

### 3. Data Flow

- **Initialization**: The `CacheManager` is initialized with configuration settings.

- **Cache Management**: Methods like `get_cache_key`, `get_cached_result`, `cache_result`, and `clear_cache` handle the caching logic.

- **Metadata Management**: The `_load_metadata` and `_save_metadata` methods manage metadata related to cache entries.

### 4. Dependencies

- **Internal Dependencies**: The `CacheManager` and `GenerationCache` classes depend on each other.

- **External Dependencies**: The code uses standard library modules like `hashlib`, `json`, `time`, and `pathlib`.

### 5. Interfaces

- **Public Methods**: The `CacheManager` and `GenerationCache` classes expose methods like `get_cache_key`, `get_cached_result`, `cache_result`, `clear_cache`, `get_model`, and `set_model`.

- **Configuration**: The `CacheManager` accepts a `config` dictionary during initialization.

### 6. Extensibility

- **Configuration**: The `CacheManager` and `GenerationCache` classes are extensible via configuration settings.

- **New Features**: Adding new cache types or configurations can be done by extending the `CacheManager` class.

### 7. Design Principles

- **SOLID Principles**: The code adheres to several SOLID principles:
  - **Single Responsibility Principle**: Each class has a single responsibility (e.g., managing cache for generation results and models).
  - **Open/Closed Principle**: The `CacheManager` and `GenerationCache` classes are open for extension (e.g., adding new cache types) but closed for modification.
  - **Liskov Substitution Principle**: The `CacheManager` and `GenerationCache` classes can be substituted for each other where applicable.
  - **Interface Segregation Principle**: The interfaces are well-defined and not overly broad.
  - **Dependency Inversion Principle**: High-level modules do not depend on low-level modules; both depend on abstractions.

- **Separation of Concerns**: The code is well-separated into classes for cache management, metadata handling, and cache operations.

### 8. Potential Improvements

- **Error Handling**: Improve error handling to make the code more robust and handle various edge cases gracefully.

- **Performance Optimization**: Consider optimizations for cache cleanup and metadata updates, especially for large caches.

- **Documentation**: Enhance documentation to include more detailed explanations of the design and usage of the cache system.

- **Unit Tests**: Implement unit tests to cover various scenarios and ensure the correctness of the cache logic.

Overall, the code is well-structured and follows good software design principles, making it extensible and maintainable.

---

*Generated by DocGenAI using mlx backend*
