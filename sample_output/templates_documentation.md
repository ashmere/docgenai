# Documentation: templates.py

## Overview

The `TemplateManager` class in the `src/docgenai/templates.py` file is designed to handle the management of Jinja2 templates for documentation generation within the DocGenAI project. This class provides functionalities to load and render templates with context data, supporting both built-in templates and custom template directories.
It also includes methods for rendering documentation, directory summaries, and footers, with fallback mechanisms to default templates when necessary. Additionally, it offers utilities for loading, saving, and listing templates, as well as creating default templates if they don't already exist.

## Key Components

1. **TemplateManager Class**:
    - ****init****: Initializes the template manager with configuration settings, ensuring the template directory exists and setting up the Jinja2 environment with the appropriate loader.
    - **_format_size**: A helper method to format file size in human-readable format.
    - **_format_duration**: A helper method to format duration in human-readable format.
    - **render_documentation**: Renders the main documentation template with provided context data.
    - **render_directory_summary**: Renders the directory summary template with provided context data.
    - **render_footer**: Renders the footer template based on the configuration, using either the extended or default footer.
    - **_render_default_documentation**: Renders the default documentation template when the specified template is not found.
    - **_render_default_directory_summary**: Renders the default directory summary template when the specified template is not found.
    - **_render_default_footer**: Renders the default footer template when the specified template is not found.
    - **_clean_markdown**: Cleans up markdown formatting to avoid lint issues.
    - **load_template**: Loads a template file as raw text, raising a `FileNotFoundError` if the template doesn't exist.
    - **save_template**: Saves a template file with the given content.
    - **list_templates**: Lists available template files in the template directory.
    - **create_default_templates**: Creates default template files if they don't already exist.

## Architecture

The `TemplateManager` class is built around the Jinja2 templating engine, utilizing a `FileSystemLoader` to load templates from a specified directory. It supports custom templates and provides methods to render documentation, directory summaries, and footers with context-specific data. The class also includes fallback mechanisms to default templates when custom templates are not available.

## Usage Examples

To use the `TemplateManager` class, you would typically initialize it with a configuration dictionary that specifies the template directory and other settings. Here's a basic example of how to use the `TemplateManager` to render a documentation template:

```python
from pathlib import Path
from docgenai.templates import TemplateManager

config = {
    "directory": Path("custom_templates").absolute(),
    "doc_template": "custom_doc_template.md",
}

template_manager = TemplateManager(config)

context = {
    "file_name": "example_file.py",
    "file_path": "path/to/example_file.py",
    "language": "Python",
    "generation_time": "2023-01-01 12:00:00",
    "model_info": {
        "name": "DocGenAI-v1",
        "backend": "Jinja2",
    },
    "documentation": "This is the documentation for the example file.",
}

rendered_documentation = template_manager.render_documentation(context)
print(rendered_documentation)

```

## Dependencies

- **Jinja2**: The class heavily relies on Jinja2 for template rendering.

- **Pathlib**: Used for handling file paths.

## Configuration

The `TemplateManager` class can be configured via a dictionary passed to its constructor, with the following keys:

- `directory`: Specifies the directory where templates are stored.

- `doc_template`: The name of the main documentation template.

- `directory_summary_template`: The name of the directory summary template.

- `footer_template`: The name of the default footer template.

- `extended_footer_template`: The name of the extended footer template (optional).

- `use_extended_footer`: A boolean flag to determine whether to use the extended footer template.

## Error Handling

The `TemplateManager` class handles errors related to template loading by raising a `TemplateNotFound` exception when the specified template cannot be found. Additionally, it ensures that the template directory exists and is writable.

## Performance Considerations

To optimize performance, consider the following:

- Ensure that the template directory is efficiently managed and that templates are not excessively large, as this could impact rendering performance.

- Minimize the use of complex expressions and filters within templates to reduce processing time.

By following these guidelines, you can effectively manage and use templates within the DocGenAI project, ensuring that documentation generation is both efficient and user-friendly.

## Architecture Analysis

## Architectural Analysis of `src/docgenai/templates.py`

### 1. Architectural Patterns

The code primarily follows a **Model-View-Controller (MVC)** pattern, although it's not explicitly named as such. The `TemplateManager` class acts as the controller, handling the logic for loading and rendering templates, while the `Environment` and `FileSystemLoader` from Jinja2 are used to manage the templates and views.

### 2. Code Organization

The code is organized into several components:

- **TemplateManager**: Centralizes template management, including loading, rendering, and configuration.

- **TemplateLoader**: Backward compatibility wrapper for `TemplateManager`.

- **Template Management**: Handles Jinja2 templates, including custom filters and template directories.

- **Default Templates**: Provides default templates for documentation and directory summaries.

- **Configuration**: Handles template configuration and paths.

### 3. Data Flow

- **Initialization**: The `TemplateManager` is initialized with configuration settings, including template directories and names.

- **Template Loading**: Templates are loaded from the specified directory or default templates if not found.

- **Rendering**: Templates are rendered with context data, including file paths, statistics, and documentation content.

- **Footer Rendering**: Footers are dynamically selected based on configuration and included in the final output.

### 4. Dependencies

- **Internal Dependencies**: The `TemplateManager` and `TemplateLoader` classes depend on each other and on Jinja2 for template management.

- **External Dependencies**: Jinja2 is an external dependency used for template rendering.

### 5. Interfaces

- **Public Methods**:
  - `TemplateManager.render_documentation`: Renders the main documentation template.
  - `TemplateManager.render_directory_summary`: Renders the directory summary template.
  - `TemplateManager.render_footer`: Renders the footer template.
  - `TemplateManager.load_template`: Loads a template from the filesystem.
  - `TemplateManager.save_template`: Saves a template to the filesystem.
  - `TemplateManager.list_templates`: Lists available templates.

- **Configuration**: The `config` dictionary is used to configure the `TemplateManager` with settings like template directories and names.

### 6. Extensibility

- **Custom Templates**: Allows custom templates to be placed in a specified directory, overriding default templates.

- **Custom Filters**: Provides custom filters (`_format_size` and `_format_duration`) that can be extended or modified.

- **Default Templates**: Includes default templates for documentation and directory summaries, which can be overridden by custom templates.

### 7. Design Principles

- **SOLID Principles**: The code adheres to several SOLID principles:
  - **Single Responsibility Principle**: The `TemplateManager` handles template management.
  - **Open/Closed Principle**: Templates and filters are open for extension but closed for modification.
  - **Liskov Substitution Principle**: The `TemplateManager` and `TemplateLoader` classes can be substituted without affecting the system's behavior.
  - **Interface Segregation Principle**: The interfaces are well-defined and not overly broad.
  - **Dependency Inversion Principle**: High-level modules depend on abstractions rather than concrete implementations.

- **Separation of Concerns**: The code is well-separated into concerns such as template management, rendering, and configuration.

### 8. Potential Improvements

- **Error Handling**: Improve error handling for template loading and rendering to handle errors gracefully.

- **Configuration Management**: Enhance configuration management to allow more flexible and dynamic configurations.

- **Testing**: Implement unit tests to cover the functionality of the `TemplateManager` and related classes.

- **Documentation**: Improve and expand documentation, especially for customizing templates and filters.

- **Performance Optimization**: Consider optimizations for loading and rendering templates, especially for large projects.

Overall, the code is well-structured and follows good software design principles, making it extensible and maintainable.

---

*Generated by DocGenAI using mlx backend*
