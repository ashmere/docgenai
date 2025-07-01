# Documentation: base_prompts.py

## Overview

This code defines a base class `BasePromptBuilder` for creating prompt templates in a structured manner, suitable for use in the DocGenAI application. The class includes shared formatting rules and a method to detect the programming language from a file extension. Subclasses can implement the `build_prompt` method to customize the prompt creation process.

## Key Components

- **BasePromptBuilder**: The main class that provides shared formatting rules and a method to detect the programming language from a file extension.

- **MARKDOWN_FORMATTING_RULES**: A class attribute containing Markdown formatting rules applicable to all documentation.

- **COMMON_GUIDELINES**: A class attribute containing common guidelines applicable to all prompts.

- **get_language_from_extension**: A static method that maps file extensions to their corresponding programming languages.

- **build_prompt**: A method that must be implemented by subclasses to build prompts with specific formatting rules.

## Architecture

The `BasePromptBuilder` class is designed to be a base class for creating prompt templates. It includes shared formatting rules and a method to detect the programming language from a file extension. Subclasses can implement the `build_prompt` method to customize the prompt creation process.
The `get_language_from_extension` method helps in identifying the appropriate programming language for the documentation.

## Usage Examples

Here's an example of how to use the `BasePromptBuilder` class to build a prompt:

```python
class MyPromptBuilder(BasePromptBuilder):
    def build_prompt(self, **kwargs) -> str:
        # Custom implementation of build_prompt
        pass

# Instantiate the subclass

prompt_builder = MyPromptBuilder()
language = prompt_builder.get_language_from_extension(".py")
print(f"Detected language: {language}")

In this example, `MyPromptBuilder` is a subclass of `BasePromptBuilder` that implements the `build_prompt` method. The `get_language_from_extension` method is used to detect the programming language from the file extension `.py`.

```

## Dependencies

This code does not depend on any external libraries or modules. It is a standalone implementation for building prompt templates in DocGenAI.

## Configuration

No configuration options or environment variables are required for this code.

## Error Handling

Errors are handled by raising `NotImplementedError` in the `build_prompt` method, which must be implemented by subclasses. This ensures that any attempt to use the `BasePromptBuilder` class directly will result in an error until a subclass is provided.

## Performance Considerations

The `get_language_from_extension` method is a static method that maps file extensions to programming languages. It is efficient and should not pose performance issues for typical use cases. The `build_prompt` method, being abstract, must be implemented by subclasses to handle prompt creation, and it should be optimized for performance based on the specific requirements of the prompts.

## Overview (2)

This code defines a base class `BasePromptBuilder` for creating prompt templates in a structured manner, suitable for use in the DocGenAI application. The class includes shared formatting rules and a method to detect the programming language from a file extension. Subclasses can implement the `build_prompt` method to customize the prompt creation process.

## Key Components (2)

- **BasePromptBuilder**: The main class that provides shared formatting rules and a method to detect the programming language from a file extension.

- **MARKDOWN_FORMATTING_RULES**: A class attribute containing Markdown formatting rules applicable to all documentation.

- **COMMON_GUIDELINES**: A class attribute containing common guidelines applicable to all prompts.

- **get_language_from_extension**: A static method that maps file extensions to their corresponding programming languages.

- **build_prompt**: A method that must be implemented by subclasses to build prompts with specific formatting rules.

## Architecture (2)

The `BasePromptBuilder` class is designed to be a base class for creating prompt templates. It includes shared formatting rules and a method to detect the programming language from a file extension. Subclasses can implement the `build_prompt` method to customize the prompt creation process.
The `get_language_from_extension` method helps in identifying the appropriate programming language for the documentation.

## Usage Examples (2)

Here's an example of how to use the `BasePromptBuilder` class to build a prompt:

```python
class MyPromptBuilder(BasePromptBuilder):
    def build_prompt(self, **kwargs) -> str:
        # Custom implementation of build_prompt
        pass

# Instantiate the subclass (2)

prompt_builder = MyPromptBuilder()
language = prompt_builder.get_language_from_extension(".py")
print(f"Detected language: {language}")

In this example, `MyPromptBuilder` is a subclass of `BasePromptBuilder` that implements the `build_prompt` method. The `get_language_from_extension` method is used to detect the programming language from the file extension `.py`.

```

## Dependencies (2)

This code does not depend on any external libraries or modules. It is a standalone implementation for building prompt templates in DocGenAI.

## Configuration (2)

No configuration options or environment variables are required for this code.

## Error Handling (2)

Errors are handled by raising `NotImplementedError` in the `build_prompt` method, which must be implemented by subclasses. This ensures that any attempt to use the `BasePromptBuilder` class directly will result in an error until a subclass is provided.

## Performance Considerations (2)

The `get_language_from_extension` method is a static method that maps file extensions to programming languages. It is efficient and should not pose performance issues for typical use cases. The `build_prompt` method, being abstract, must be implemented by subclasses to handle prompt creation, and it should be optimized for performance based on the specific requirements of the prompts.

## Architecture Analysis

## Architectural Analysis

### 1. Architectural Patterns

The provided code does not explicitly use a known design pattern such as MVC (Model-View-Controller), Observer, Factory, or others. It is a straightforward implementation of a base class with static methods and a method that raises an error if not overridden by a subclass.
This structure is typical for a base class in an object-oriented design, where the methods are meant to be overridden by subclasses to provide specific functionality.

### 2. Code Organization

The code is organized into a single file, `base_prompts.py`, which contains a base class `BasePromptBuilder` with static attributes and methods. The class includes constants for Markdown formatting rules and common guidelines for all prompts. The `get_language_from_extension` method is static and uses a dictionary to map file extensions to programming languages.
The `build_prompt` method is abstract and must be overridden by subclasses.

### 3. Data Flow

- **Inputs**: The `build_prompt` method expects keyword arguments (`**kwargs`) which are used to construct the prompt.

- **Outputs**: The `build_prompt` method returns a string that represents the constructed prompt.

- **Processing**: The `get_language_from_extension` method processes the file extension to determine the appropriate programming language for code examples.

### 4. Dependencies

- **Internal Dependencies**: The `BasePromptBuilder` class depends on itself for the `build_prompt` method, which is abstract and must be overridden by subclasses.

- **External Dependencies**: The class does not depend on any external libraries or modules.

### 5. Interfaces

- **Public API**: The only public interface provided by the `BasePromptBuilder` class is the `build_prompt` method, which must be overridden by subclasses to provide specific functionality.

- **Subclasses**: Subclasses must implement the `build_prompt` method to adhere to the abstract base class definition.

### 6. Extensibility

The code is designed to be extensible. Subclasses can override the `build_prompt` method to customize the prompt construction process. This adheres to the open/closed principle, allowing for future modifications without changing the existing code.

### 7. Design Principles

- **SOLID Principles**: The `BasePromptBuilder` class follows the Single Responsibility Principle by encapsulating only the shared formatting rules and methods related to prompt construction. The Open/Closed Principle is followed by allowing subclasses to extend the functionality without modifying the base class.

- **Separation of Concerns**: The code separates concerns related to prompt construction and Markdown formatting from the logic of detecting programming languages from file extensions.

### 8. Potential Improvements

- **Documentation**: Adding more detailed comments and docstrings, especially for the `build_prompt` method and the `get_language_from_extension` method, would improve the understandability of the code.

- **Error Handling**: Implementing error handling in the `build_prompt` method and `get_language_from_extension` method would make the class more robust and resilient to unexpected inputs.

- **Subclassing**: Providing more detailed examples or a default implementation for the `build_prompt` method in the `BasePromptBuilder` class could guide developers on how to use and extend the base class effectively.

## Conclusion

The `BasePromptBuilder` class in `src/docgenai/prompts/base_prompts.py` is a basic implementation of an abstract base class in Python, suitable for use as a template for creating more specific prompt builders in subclasses. The design follows basic object-oriented principles and provides a clear interface for subclasses to implement specific prompt construction logic.

---

*Generated by DocGenAI using mlx backend*
