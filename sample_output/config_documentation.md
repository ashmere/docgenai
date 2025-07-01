# Documentation: config.py

## Overview

The `config.py` file is a part of the DocGenAI project and is responsible for managing configuration settings. It handles loading configuration from YAML files, environment variables, and provides sensible defaults for all settings. The configuration supports the new DeepSeek-Coder models and includes platform-aware settings.

## Key Components

1. **`get_default_config()`**: Generates a default configuration dictionary with platform-aware settings.

2. **`merge_configs(base, override)`**: Recursively merges configuration dictionaries.

3. **`apply_env_overrides(config)`**: Applies environment variable overrides to the configuration.

4. **`_convert_env_value(env_value)`**: Converts environment variable string to appropriate type.

5. **`load_config(config_path=None)`**: Loads configuration with hierarchy: defaults -> file -> environment.

6. **`validate_config(config)`**: Validates and normalizes configuration values.

7. **`get_model_config(config)`**: Extracts and prepares model-specific configuration.

8. **`get_cache_config(config)`**: Extracts cache configuration.

9. **`get_output_config(config)`**: Extracts output configuration.

10. **`get_generation_config(config)`**: Extracts generation configuration.

11. **`create_default_config_file(path='config.yaml')`**: Creates a default configuration file with comprehensive settings.

12. **`load_model_config(config_path=None)`**: Loads configuration and returns model-specific settings.

## Architecture

The `config.py` file follows a modular approach to configuration management. It starts by defining default configurations and then allows for hierarchical merging and environment variable overrides.
The configuration is structured to be easily extendable and customizable, with specific sections for models, cache, output, generation, logging, security, performance, integrations, and experimental settings.

## Usage Examples

To use the configuration management system, you can call `load_config()` with a configuration file path if you want to use a custom configuration. For example:

```python
config = load_config("path/to/config.yaml")

This will load the configuration from the specified file, apply any environment variable overrides, and validate the configuration settings.

```

## Dependencies

- `os`: For environment variable management.

- `platform`: For platform-specific settings.

- `pathlib`: For path manipulation.

- `yaml`: For YAML file parsing.

- `dotenv`: For loading environment variables from a `.env` file.

## Configuration

- Configuration can be set via environment variables by prefixing the key with `DOCGENAI_` and using double underscores to separate nested keys. For example: `DOCGENAI_MODEL__TEMPERATURE=0.8`.

- Environment variables can also be set directly in your operating system's environment settings.

## Error Handling

Errors are handled by raising `ValueError` for invalid configuration settings. Common issues include incorrect types or values for configuration parameters.

## Performance Considerations

Performance is optimized by limiting the number of concurrent file processing tasks and setting reasonable timeouts for processing. The system also supports GPU acceleration where applicable, and it can automatically detect and use GPUs if enabled.

## Configuration Management for DocGenAI

Handles loading configuration from YAML files, environment variables, and provides sensible defaults for all settings with comprehensive support for the new DeepSeek-Coder models and platform-aware settings.

## Architecture Analysis

## Architectural Analysis of `src/docgenai/config.py`

### 1. Architectural Patterns

The code does not explicitly use a known design pattern such as MVC, Observer, Factory, etc. Instead, it follows a modular approach with functions and configurations loaded from YAML files, environment variables, and defaults.

### 2. Code Organization

The code is organized into several functions and configurations:

- **Default Configuration**: `get_default_config()` provides a base configuration with sensible defaults.

- **Merge Configurations**: `merge_configs()` recursively merges configurations.

- **Environment Overrides**: `apply_env_overrides()` applies environment variable overrides.

- **Configuration Loading**: `load_config()` loads configuration hierarchically.

- **Validation**: `validate_config()` validates and normalizes configuration values.

- **Model and Cache Configuration**: Helper functions like `get_model_config()`, `get_cache_config()`, and `get_output_config()` extract specific parts of the configuration.

- **Default Config File Creation**: `create_default_config_file()` generates a default configuration file.

### 3. Data Flow

- **Loading Configuration**: The configuration is loaded from `config.yaml` if provided, default settings are used otherwise.

- **Environment Variables**: Environment variables are applied to override settings.

- **Validation**: Configuration values are validated to ensure they meet specific criteria.

- **Extraction**: Helper functions extract specific parts of the configuration for use in other modules.

### 4. Dependencies

- **Internal Dependencies**: The code depends on standard library modules like `os`, `platform`, `pathlib`, `yaml`, and `dotenv`.

- **External Dependencies**: The code does not depend on any third-party libraries.

### 5. Interfaces

- **Public Functions**:
  - `load_config()`: Loads configuration from files and environment variables.
  - `validate_config()`: Validates and normalizes configuration values.
  - `get_model_config()`, `get_cache_config()`, `get_output_config()`, `get_generation_config()`: Extract specific parts of the configuration.
  - `create_default_config_file()`: Creates a default configuration file.

- **Configuration Data**: The configuration is stored in a hierarchical dictionary structure, which is accessed and modified through functions.

### 6. Extensibility

- **Configuration Overrides**: Configuration can be overridden via environment variables, providing flexibility.

- **Default Settings**: The default configuration is comprehensive, allowing for customization via overrides.

- **Future Extensions**: The code is structured to allow for easy extension, for example, by adding more configuration options or modifying the validation logic.

### 7. Design Principles

- **SOLID Principles**: The code adheres to some SOLID principles, particularly the Single Responsibility Principle (SRP) by separating concerns into different functions.

- **Separation of Concerns**: The code is well-organized, with each function having a clear responsibility.

- **Encapsulation**: Configuration values are encapsulated within functions, ensuring they are not exposed directly.

### 8. Potential Improvements

- **Configuration Management**: Consider using a more robust configuration management library like `pydantic` for better configuration handling and validation.

- **Logging**: Improve logging to include more detailed information, especially for debugging purposes.

- **Error Handling**: Enhance error handling to provide more informative messages and handle edge cases more gracefully.

- **Performance**: Optimize performance-related settings and consider adding more performance metrics and monitoring.

Overall, the code is well-structured and follows good software design principles, making it extensible and maintainable.

---

*Generated by DocGenAI using mlx backend*
