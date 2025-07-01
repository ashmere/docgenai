# Documentation: config.py

## Overview

The `config.py` file is a crucial part of the DocGenAI project, responsible for managing configuration settings. It handles the loading of configuration from YAML files, environment variables, and provides default configurations tailored for the new DeepSeek-Coder models and platform-aware settings.
The configuration includes settings for models, cache, output, templates, generation, logging, security, performance, integrations, chaining, and experimental features.

## Key Components

1. **`get_default_config()`**: Generates a default configuration dictionary with platform-aware settings.

2. **`merge_configs(base, override)`**: Recursively merges two configuration dictionaries.

3. **`apply_env_overrides(config)`**: Applies environment variable overrides to the configuration.

4. **`_convert_env_value(env_value)`**: Converts environment variable strings to appropriate types.

5. **`load_config(config_path=None)`**: Loads configuration with hierarchy: defaults -> file -> environment.

6. **`validate_config(config)`**: Validates and normalizes configuration values.

7. **`get_model_config(config)`**: Extracts and prepares model-specific configuration.

8. **`get_cache_config(config)`**: Extracts cache configuration.

9. **`get_output_config(config)`**: Extracts output configuration.

10. **`get_generation_config(config)`**: Extracts generation configuration.

11. **`create_default_config_file(path="config.yaml")`**: Creates a default configuration file with comprehensive settings.

12. **`load_model_config(config_path=None)`**: Loads configuration and returns model-specific settings.

## Architecture

The configuration management system in `config.py` is designed to be modular and hierarchical. The `load_config` function starts by loading default configurations and then applies any overrides specified in a provided configuration file or environment variables.
The `apply_env_overrides` function ensures that environment variables are used to override settings, which is particularly useful for platform-specific configurations.

## Usage Examples

To use the configuration system, you can call `load_config()` with a path to a configuration file if you want to use a custom configuration. For example:

```python
config = load_config("path/to/config.yaml")

This will load the configuration from the specified file, and if not provided, it will look for a default `config.yaml` file in the current directory.

To use environment variables to override settings, ensure that your environment variables are prefixed with `DOCGENAI_` and use double underscores to separate nested keys. For example, to override the `temperature` setting for the model, you can set the environment variable `DOCGENAI_MODEL__TEMPERATURE=0.8`.

```

## Dependencies

- `os`: For environment variable management.

- `platform`: For platform-specific settings.

- `pathlib`: For path manipulation.

- `yaml`: For parsing YAML configuration files.

- `dotenv`: For loading environment variables from a `.env` file.

## Configuration

- `config.yaml`: A YAML file where you can specify overrides for default settings.

- Environment variables: Use `DOCGENAI_` as a prefix and double underscores to specify nested keys. For example, `DOCGENAI_MODEL__TEMPERATURE=0.8`.

## Error Handling

Errors are handled by raising `ValueError` for invalid configurations. The `validate_config` function ensures that the configuration values meet the required criteria.

## Performance Considerations

Performance is optimized by limiting the number of concurrent file processing tasks and by setting reasonable limits on memory usage and file processing time. The `max_concurrent_files`, `max_memory_usage_gb`, and `processing_timeout_minutes` settings can be adjusted to fine-tune performance based on the system's capabilities.

## Summary

The `config.py` file provides a comprehensive system for managing configuration settings in the DocGenAI project, ensuring that it can be easily customized for different platforms and configurations, while also supporting platform-specific optimizations.

## Architecture Analysis

## Architectural Analysis of `src/docgenai/config.py`

### 1. Architectural Patterns

The code primarily follows a **Model-View-Controller (MVC)** pattern, although it's not explicitly named in the comments, it's evident from the separation of concerns:

- **Model**: Handles the configuration data and logic, represented by `get_default_config`, `merge_configs`, `apply_env_overrides`, `validate_config`, `get_model_config`, `get_cache_config`, `get_output_config`, `get_generation_config`.

- **View**: Not explicitly present in the code, but the configuration data is structured in a hierarchical manner that could be considered a simplified view of the configuration settings.

- **Controller**: The `load_config` function acts as the controller, orchestrating the loading and merging of configuration settings from various sources.

### 2. Code Organization

The code is well-organized into several functions, each serving a specific purpose:

- **Configuration Loading**: Functions like `get_default_config`, `merge_configs`, `apply_env_overrides`, `validate_config`, `load_config`.

- **Environment Variables Handling**: Functions like `_convert_env_value`.

- **Platform-Aware Settings**: Functions like `get_model_config`, `get_cache_config`, `get_output_config`, `get_generation_config`.

- **Default Configuration Creation**: `create_default_config_file`.

### 3. Data Flow

- **Default Configuration**: The `get_default_config` function provides a default configuration dictionary.

- **Configuration Merging**: The `merge_configs` function merges base and override configurations.

- **Environment Variable Overrides**: The `apply_env_overrides` function applies environment variables to the configuration.

- **Validation**: The `validate_config` function ensures the configuration values meet certain criteria.

- **Configuration Loading**: The `load_config` function loads the configuration from a file and applies environment overrides.

### 4. Dependencies

- **Internal Dependencies**: The code depends on standard library modules like `os`, `platform`, `pathlib`, `yaml`, and `dotenv`.

- **External Dependencies**: None, except for the `yaml` and `dotenv` modules, which are part of the standard library in Python.

### 5. Interfaces

- **Public Functions**:
  - `load_config`: Loads the configuration from a file or defaults.
  - `validate_config`: Validates the configuration.
  - `get_model_config`, `get_cache_config`, `get_output_config`, `get_generation_config`: Extracts specific parts of the configuration.
  - `create_default_config_file`: Creates a default configuration file.

- **Configuration Data**: The configuration data is structured in a hierarchical dictionary, which provides a clear and organized way to manage settings.

### 6. Extensibility

The code is designed to be extensible:

- **Adding New Configurations**: New configurations can be added by extending the `get_default_config` function.

- **Environment Variables**: The `apply_env_overrides` function allows for dynamic configuration via environment variables.

- **Configuration Files**: The `load_config` function supports loading configurations from a file.

### 7. Design Principles

- **SOLID Principles**: The code adheres to several SOLID principles:
  - **Single Responsibility Principle**: Each function has a single responsibility.
  - **Open/Closed Principle**: The code is open for extension (e.g., new configurations can be added) but closed for modification (existing code is not modified).
  - **Liskov Substitution Principle**: The functions operate on the configuration dictionary, which can be replaced with another configuration dictionary of the same structure.
  - **Interface Segregation Principle**: The functions operate on the configuration dictionary, not on specific parts of it.
  - **Dependency Inversion Principle**: The code does not depend on specific implementations but on abstractions (e.g., `Dict[str, Any]`).

- **Separation of Concerns**: The configuration loading, merging, and validation are separated from the logic that uses the configuration.

### 8. Potential Improvements

- **Configuration Validation**: The `validate_config` function could be enhanced to include more detailed validation rules.

- **Error Handling**: Improve error handling for file operations and YAML parsing.

- **Logging**: Add more detailed logging for configuration loading and validation.

- **Environment Variable Handling**: Consider using a more robust library for handling environment variables.

- **Configuration File Format**: Consider supporting more configuration file formats like JSON or TOML for flexibility.

Overall, the code is well-structured and follows good software design principles, making it easy to extend and maintain.

---

*Generated by DocGenAI using mlx backend*
