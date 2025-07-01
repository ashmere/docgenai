# Documentation: cache.py

## Overview

The `cache.py` module provides caching utilities for `DocGenAI` to improve performance by storing frequently used data, such as generation results and model instances, in memory or on disk. This helps in avoiding expensive recomputation and reloading operations, enhancing the efficiency of the application.

## Key Components

1. **CacheManager Class**:
   - **Purpose**: Manages caching for generation results and model instances.
   - **Attributes**:
     - `enabled`: Boolean to enable or disable caching.
     - `cache_dir`: Directory where cached data is stored.
     - `max_size_mb`: Maximum size of the cache in megabytes.
     - `ttl_hours`: Time-to-live (TTL) for cached entries in hours.
   - **Methods**:
     - `**init**(config: Dict[str, Any])`: Initializes the cache manager with configuration.
     - `_load_metadata()`: Loads cache metadata from disk.
     - `_save_metadata()`: Saves cache metadata to disk.
     - `get_cache_key(file_path: str, include_architecture: bool = True) -> str`: Generates a cache key from the file content and options.
     - `_get_cache_path(cache_key: str) -> Path`: Returns the file path for a cache entry.
     - `_is_expired(entry_info: Dict[str, Any]) -> bool`: Checks if a cache entry is expired.
     - `_cleanup_cache()`: Removes old cache entries if the cache size exceeds the limit.
     - `_remove_cache_entry(cache_key: str)`: Removes a single cache entry.
     - `get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]`: Retrieves a cached generation result.
     - `cache_result(cache_key: str, result: Dict[str, Any])`: Caches a generation result.
     - `clear_cache()`: Clears all cache entries.
     - `get_stats() -> Dict[str, Any]`: Gets cache statistics.

2. **GenerationCache Class**:
   - **Purpose**: Backward compatibility wrapper for `CacheManager`.
   - **Methods**:
     - `**init**(cache_dir: Path, max_size_mb: int = 1000)`: Initializes the `CacheManager` with the provided configuration.
     - `get(content: str, prompt_type: str = "default") -> Optional[str]`: Retrieves cached content based on the provided content and prompt type.
     - `set(content: str, result: str, prompt_type: str = "default")`: Caches the provided content and result.
     - `clear()`: Clears the cache.

3. **ModelCache Class**:
   - **Purpose**: Handles session-level model caching.
   - **Methods**:
     - `**init**()`: Initializes the `ModelCache`.
     - `get_model(model_name: str, config: Any)`: Retrieves a cached model if it matches the requested configuration.
     - `set_model(model_name: str, model: Any, config: Any)`: Caches a model for the session.
     - `clear()`: Clears the cached model.

## Architecture

The `CacheManager` class is the core of the caching system, handling both generation results and model instances. It uses a directory on disk to store cached data, with each entry identified by a unique cache key. The `get_cache_key` method generates this key from the file content and options, while `cache_result` stores the result in a JSON file.
The `_cleanup_cache` method ensures that the cache does not grow too large by removing expired entries and old entries when the size limit is reached.

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

# Generate a cache key for a file

cache_key = cache_manager.get_cache_key("path/to/your/file.txt")

# Check if the result is already cached

cached_result = cache_manager.get_cached_result(cache_key)
if cached_result is None:
    # Perform the expensive operation and cache the result
    result = generate_expensive_result()
    cache_manager.cache_result(cache_key, result)
else:
    # Use the cached result
    result = cached_result

```

## Dependencies

- `hashlib`: For generating content hashes.

- `json`: For serializing and deserializing cache entries.

- `pathlib`: For file path operations.

- `typing`: For type hints.

## Configuration

- `enabled`: Enables or disables caching.

- `directory`: Directory where cached data is stored.

- `max_size_mb`: Maximum size of the cache in megabytes.

- `ttl_hours`: Time-to-live (TTL) for cached entries in hours.

## Error Handling

- Errors related to file operations (e.g., reading or writing files) are handled by catching `IOError`.

- Errors related to JSON serialization or deserialization are handled by catching `json.JSONDecodeError`.

## Performance Considerations

- Caching is beneficial for performance, especially for expensive operations like generating documentation.

- The `_cleanup_cache` method ensures that the cache does not grow too large by periodically removing old entries.

- The `get_cached_result` method checks for cache entries before performing expensive operations, reducing redundant computations.

## Architecture Analysis

## Architectural Analysis of `src/docgenai/cache.py`

### 1. Architectural Patterns

The code primarily follows a **Singleton pattern** for the `CacheManager` class, ensuring that only one instance of the cache manager is used throughout the application. This is evident from the `**init**` method where it checks if an instance already exists and returns it if it does.

### 2. Code Organization

The code is organized into several classes and methods:

- **CacheManager**: Manages the cache for generation results and model instances.

- **GenerationCache**: A backward compatibility wrapper for `CacheManager`.

- **ModelCache**: Handles session-level model caching.

### 3. Data Flow

- **Initialization**: The `CacheManager` is initialized with configuration settings.

- **Cache Management**: Methods like `get_cache_key`, `cache_result`, and `get_cached_result` handle the caching and retrieval of data.

- **Metadata Management**: The `_load_metadata` and `_save_metadata` methods manage metadata about cache entries.

- **Cache Cleanup**: The `_cleanup_cache` method ensures that the cache does not exceed its size limit.

### 4. Dependencies

- **Internal Dependencies**: The `CacheManager` and `GenerationCache` classes depend on each other.

- **External Dependencies**: The code uses standard library modules like `hashlib`, `json`, `pathlib`, and `typing`.

### 5. Interfaces

- **Public Methods**: The `CacheManager` and `GenerationCache` classes expose methods for caching and retrieving data.

- **Configuration**: The `**init**` method of `CacheManager` accepts a configuration dictionary.

### 6. Extensibility

- **Configuration**: The `**init**` method of `CacheManager` allows for easy configuration changes.

- **Cache Management**: Methods like `cache_result` and `get_cached_result` can be extended to support more types of cached data.

### 7. Design Principles

- **SOLID Principles**: The code adheres to several SOLID principles:
  - **Single Responsibility Principle**: Each class has a single responsibility (e.g., managing cache for generation results).
  - **Open/Closed Principle**: The `CacheManager` and `GenerationCache` classes are open for extension (e.g., through method overrides) but closed for modification.
  - **Liskov Substitution Principle**: The `CacheManager` and `GenerationCache` classes can be substituted for each other in the context of the application.
  - **Interface Segregation Principle**: The interfaces are well-defined and not overly broad.
  - **Dependency Inversion Principle**: High-level modules do not depend on low-level modules; both depend on abstractions.

- **Separation of Concerns**: The code is well-separated into classes and methods, each performing a specific task.

### 8. Potential Improvements

- **Error Handling**: Improve error handling to make it more robust, especially in scenarios where file operations fail.

- **Performance Optimization**: Consider optimizations for cache cleanup and metadata management, especially for large caches.

- **Configuration Validation**: Add validation for the configuration settings to ensure they are valid and expected types.

- **Unit Tests**: Implement unit tests to cover various scenarios and edge cases, ensuring the reliability of the code.

Overall, the code is well-structured and follows good software design principles, making it extensible and maintainable.

---

*Generated by DocGenAI using mlx backend*
