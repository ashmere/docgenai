"""
Documentation generation prompt templates with multi-audience support.
"""

from pathlib import Path
from typing import Dict, Optional

from .base_prompts import BasePromptBuilder


class DocumentationPromptBuilder(BasePromptBuilder):
    """Builder for documentation generation prompts with multi-audience support."""

    # Project type templates for different architectural patterns
    PROJECT_TEMPLATES = {
        "microservice": {
            "focus": ["service_boundaries", "api_contracts", "deployment"],
            "sections": [
                "Service Architecture",
                "API Documentation",
                "Deployment Guide",
            ],
        },
        "library": {
            "focus": ["public_api", "usage_patterns", "integration"],
            "sections": ["API Reference", "Usage Examples", "Integration Guide"],
        },
        "application": {
            "focus": ["user_workflows", "configuration", "operations"],
            "sections": ["User Guide", "Configuration", "Operations Manual"],
        },
        "framework": {
            "focus": ["extension_points", "patterns", "architecture"],
            "sections": ["Architecture Guide", "Extension Guide", "Best Practices"],
        },
    }

    # Developer-focused documentation sections
    DEVELOPER_SECTIONS = """
1. **System Purpose & Architecture**: Core problem this solves, architectural approach, key decisions and trade-offs
2. **Module Interaction Analysis**: How modules/packages interact and depend on each other, service boundaries, data flow
3. **Key Class Relationships**: Core abstractions and interfaces, design patterns, critical dependencies
4. **Microservices Architecture Insights**: Service boundaries, communication patterns, deployment considerations
5. **Development Guide**: How to extend the system, key patterns, architecture constraints
"""

    # User-focused documentation sections
    USER_SECTIONS = """
1. **Quick Start**: Primary use cases, installation steps, first successful run example
2. **Command Line Interface**: Available commands with examples, common usage patterns, configuration options
3. **Configuration Guide**: Environment variables, configuration file structure, common scenarios
4. **Operational Guide**: Monitoring, troubleshooting, performance considerations
"""

    # Multi-file analysis sections
    MULTI_FILE_DEVELOPER_SECTIONS = """
1. **System Purpose & Architecture**: What problem does this solve? Key architectural decisions and overall system design
2. **Module Interaction Analysis**: How do these modules/files interact and depend on each other? Service boundaries and data flow
3. **Key Class Relationships**: Core abstractions, design patterns, and critical dependency relationships
4. **Microservices Architecture Insights**: Service boundary identification, communication patterns, team ownership
5. **Development Guide**: Extension points, key patterns to follow, architecture constraints
"""

    def build_developer_prompt(
        self,
        code: str,
        file_path: str,
        language: str = None,
        project_type: str = "auto",
        is_multi_file: bool = False,
        context_info: Optional[Dict] = None,
    ) -> str:
        """
        Build developer-focused documentation prompt.

        Args:
            code: Source code to document
            file_path: Path to the source file
            language: Programming language (auto-detected if None)
            project_type: Type of project (microservice, library, application, framework)
            is_multi_file: Whether this is multi-file analysis
            context_info: Additional context from multi-file analysis

        Returns:
            Complete developer documentation prompt
        """
        if language is None:
            file_extension = Path(file_path).suffix.lower()
            language = self.get_language_from_extension(file_extension)

        sections = (
            self.MULTI_FILE_DEVELOPER_SECTIONS
            if is_multi_file
            else self.DEVELOPER_SECTIONS
        )

        project_context = ""
        if project_type != "auto" and project_type in self.PROJECT_TEMPLATES:
            template = self.PROJECT_TEMPLATES[project_type]
            project_context = f"""
**Project Type**: {project_type.title()}
**Focus Areas**: {', '.join(template['focus'])}
**Key Sections**: {', '.join(template['sections'])}
"""

        multi_file_context = ""
        if is_multi_file and context_info:
            multi_file_context = f"""
**Multi-File Analysis Context**:
- Files analyzed: {context_info.get('file_count', 'multiple')}
- Group: {context_info.get('group_name', 'N/A')}
- Total groups: {context_info.get('total_groups', 'N/A')}
"""

        prompt = f"""You are an expert software architect and technical writer.
Generate comprehensive developer documentation for software engineers with systems architecture focus.

**Analysis Level**: Module-level + Strategic Class-level
- Focus on module interactions and service boundaries
- Include only strategic/architectural classes, not implementation details
- Emphasize microservices patterns and deployment considerations

{project_context}{multi_file_context}
The documentation should include these sections:

{sections}

**Additional Guidelines**:
- Focus on "why" not just "what" - explain architectural decisions
- Identify design patterns and their rationale
- Show specific file/module interactions, not generic descriptions
- Include extension points and development guidance
- Consider microservices architecture and team ownership

{self.MARKDOWN_FORMATTING_RULES}

**File Path**: `{file_path}`

**Code**:
```{language}
{code}
```

Write the documentation directly without any markdown code block wrappers.
Start immediately with the first section:"""

        return prompt

    def build_user_prompt(
        self,
        code: str,
        file_path: str,
        language: str = None,
        project_type: str = "auto",
    ) -> str:
        """
        Build user-focused documentation prompt.

        Args:
            code: Source code to document
            file_path: Path to the source file
            language: Programming language (auto-detected if None)
            project_type: Type of project

        Returns:
            Complete user documentation prompt
        """
        if language is None:
            file_extension = Path(file_path).suffix.lower()
            language = self.get_language_from_extension(file_extension)

        prompt = f"""You are an expert technical writer focused on user experience.
Generate practical user documentation for application users.

**Focus**: Practical usage, not code implementation
- Include command-line examples, not code examples
- Focus on configuration and operational guidance
- Provide troubleshooting and common usage patterns

The documentation should include:

{self.USER_SECTIONS}

**Guidelines**:
- Use command-line examples instead of code examples
- Focus on practical usage and configuration
- Include troubleshooting and operational guidance
- Keep it accessible for non-developers

{self.MARKDOWN_FORMATTING_RULES}

**File Path**: `{file_path}`

**Code**:
```{language}
{code}
```

Write the documentation directly without any markdown code block wrappers.
Start immediately with the first section:"""

        return prompt

    def build_prompt(
        self,
        code: str,
        file_path: str,
        language: str = None,
        doc_type: str = "developer",
        project_type: str = "auto",
        is_multi_file: bool = False,
        context_info: Optional[Dict] = None,
    ) -> str:
        """
        Build documentation prompt based on audience type.

        Args:
            code: Source code to document
            file_path: Path to the source file
            language: Programming language (auto-detected if None)
            doc_type: Type of documentation (developer, user, both)
            project_type: Type of project
            is_multi_file: Whether this is multi-file analysis
            context_info: Additional context from multi-file analysis

        Returns:
            Complete documentation prompt
        """
        if doc_type == "user":
            return self.build_user_prompt(code, file_path, language, project_type)
        else:  # Default to developer
            return self.build_developer_prompt(
                code, file_path, language, project_type, is_multi_file, context_info
            )

    def build_multi_file_prompt(
        self,
        files_content: Dict[str, str],
        group_info: Dict,
        doc_type: str = "developer",
        project_type: str = "auto",
    ) -> str:
        """
        Build multi-file analysis prompt.

        Args:
            files_content: Dictionary of file_path -> content
            group_info: Information about the file group
            doc_type: Type of documentation (developer, user)
            project_type: Type of project

        Returns:
            Complete multi-file documentation prompt
        """
        files_context = ""
        for file_path, content in files_content.items():
            file_extension = Path(file_path).suffix.lower()
            language = self.get_language_from_extension(file_extension)
            files_context += f"""
**File**: `{file_path}`
```{language}
{content}
```

"""

        context_info = {
            "file_count": len(files_content),
            "group_name": group_info.get("name", "Unknown"),
            "total_groups": group_info.get("total_groups", 1),
        }

        if doc_type == "user":
            return self.build_user_multi_file_prompt(
                files_context, group_info, project_type
            )
        else:
            return self.build_developer_multi_file_prompt(
                files_context, group_info, project_type, context_info
            )

    def build_developer_multi_file_prompt(
        self,
        files_context: str,
        group_info: Dict,
        project_type: str,
        context_info: Dict,
    ) -> str:
        """Build developer-focused multi-file prompt."""
        project_context = ""
        if project_type != "auto" and project_type in self.PROJECT_TEMPLATES:
            template = self.PROJECT_TEMPLATES[project_type]
            project_context = f"""
**Project Type**: {project_type.title()}
**Focus Areas**: {', '.join(template['focus'])}
"""

        prompt = f"""You are an expert software architect analyzing multiple related files.
Generate comprehensive developer documentation with systems architecture focus.

**Analysis Instructions**:
- Analyze files together to understand relationships and interactions
- Focus on module-level interactions + strategic class relationships
- Identify service boundaries and microservices patterns
- Show how files depend on and interact with each other
- Explain design patterns and architectural decisions

{project_context}
**Multi-File Context**:
- Files in group: {context_info['file_count']}
- Group: {context_info['group_name']}
- Total groups: {context_info['total_groups']}

The documentation should include:

{self.MULTI_FILE_DEVELOPER_SECTIONS}

**Guidelines**:
- Focus on cross-file relationships and dependencies
- Identify architectural patterns across multiple files
- Explain how components work together as a system
- Include specific examples of file interactions
- Consider microservices architecture and deployment patterns

{self.MARKDOWN_FORMATTING_RULES}

**Files to Analyze**:
{files_context}

Write comprehensive documentation analyzing these files together.
Start immediately with the first section:"""

        return prompt

    def build_user_multi_file_prompt(
        self, files_context: str, group_info: Dict, project_type: str
    ) -> str:
        """Build user-focused multi-file prompt."""
        prompt = f"""You are an expert technical writer analyzing multiple application files.
Generate practical user documentation focusing on how to use this application.

**Analysis Instructions**:
- Focus on user-facing functionality across these files
- Identify command-line interfaces, configuration options, and usage patterns
- Provide practical examples of how to run and configure the application
- Include troubleshooting and operational guidance

The documentation should include:

{self.USER_SECTIONS}

**Guidelines**:
- Use command-line examples, not code examples
- Focus on practical usage and configuration
- Show how to install, configure, and operate the application
- Include troubleshooting for common issues

{self.MARKDOWN_FORMATTING_RULES}

**Files to Analyze**:
{files_context}

Write practical user documentation for this application.
Start immediately with the first section:"""

        return prompt
