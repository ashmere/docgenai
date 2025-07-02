"""
Pre-built chain configurations for common documentation generation patterns.
"""

from typing import Dict, List, Optional

from .chain import PromptChain
from .step import PromptStep, StepConfig


class ChainBuilder:
    """
    Builder for creating common prompt chain configurations.

    Provides pre-built chains for typical documentation generation patterns
    and utilities for creating custom chains.
    """

    @staticmethod
    def simple_documentation_chain() -> PromptChain:
        """
        Create a simple single-step documentation chain.

        This is equivalent to the current documentation generation behavior.

        Returns:
            PromptChain with a single documentation step
        """
        steps = [
            PromptStep(
                name="documentation",
                prompt_template="{code}\n\nGenerate documentation for this code:",
                config=StepConfig(timeout=300.0),
                metadata={"type": "simple", "version": "1.0"},
            )
        ]

        return PromptChain(
            steps=steps,
            name="SimpleDocumentation",
            fail_fast=True,
        )

    @staticmethod
    def enhanced_documentation_chain() -> PromptChain:
        """
        Create an enhanced multi-step documentation chain.

        Steps:
        1. Analyze the code structure and patterns
        2. Generate comprehensive documentation
        3. Review and enhance the documentation

        Returns:
            PromptChain with analysis, generation, and enhancement steps
        """
        steps = [
            PromptStep(
                name="analyze",
                prompt_template="""
Analyze the following code and identify:
1. Main components and their purposes
2. Key patterns and architectural decisions
3. Dependencies and relationships
4. Complexity and important details

Code:
{code}

Provide a structured analysis:""",
                config=StepConfig(timeout=180.0),
                metadata={"type": "analysis", "version": "1.0"},
            ),
            PromptStep(
                name="documentation",
                prompt_template="""
Based on this code analysis:

{analyze}

Generate comprehensive documentation for the following code:

{code}

Create well-structured documentation with clear sections:""",
                depends_on=["analyze"],
                config=StepConfig(timeout=300.0),
                metadata={"type": "generation", "version": "1.0"},
            ),
            PromptStep(
                name="enhance",
                prompt_template="""
Review and enhance this documentation:

{documentation}

Original analysis:
{analyze}

Improve the documentation by:
1. Adding missing details
2. Clarifying complex concepts
3. Ensuring consistency
4. Adding practical examples where helpful

Enhanced documentation:""",
                depends_on=["analyze", "documentation"],
                config=StepConfig(timeout=240.0),
                metadata={"type": "enhancement", "version": "1.0"},
            ),
        ]

        return PromptChain(
            steps=steps,
            name="EnhancedDocumentation",
            fail_fast=False,  # Continue even if analysis fails
        )

    @staticmethod
    def architecture_diagram_chain() -> PromptChain:
        """
        Create a chain for generating architecture documentation with diagrams.

        This is a future enhancement pattern that could be used when
        diagram support is re-added.

        Steps:
        1. Analyze code architecture
        2. Generate textual architecture description
        3. Create diagram specification
        4. Combine into final documentation

        Returns:
            PromptChain for architecture documentation with diagrams
        """
        steps = [
            PromptStep(
                name="architecture_analysis",
                prompt_template="""
Analyze the architecture of this code:

{code}

Focus on:
1. Component relationships
2. Data flow patterns
3. Key interfaces
4. Architectural patterns used

Provide detailed architectural analysis:""",
                config=StepConfig(timeout=200.0),
                metadata={"type": "architecture_analysis", "version": "1.0"},
            ),
            PromptStep(
                name="text_description",
                prompt_template="""
Based on this architectural analysis:

{architecture_analysis}

Create a comprehensive textual description of the architecture:""",
                depends_on=["architecture_analysis"],
                config=StepConfig(timeout=180.0),
                metadata={"type": "text_description", "version": "1.0"},
            ),
            PromptStep(
                name="diagram_spec",
                prompt_template="""
Based on this architectural analysis:

{architecture_analysis}

Create a specification for an architecture diagram that shows:
1. Key components
2. Relationships and dependencies
3. Data flow
4. Interface boundaries

Diagram specification:""",
                depends_on=["architecture_analysis"],
                config=StepConfig(timeout=150.0),
                metadata={"type": "diagram_spec", "version": "1.0"},
            ),
            PromptStep(
                name="combined_documentation",
                prompt_template="""
Combine these elements into comprehensive architecture documentation:

Text Description:
{text_description}

Diagram Specification:
{diagram_spec}

Original Analysis:
{architecture_analysis}

Create final architecture documentation:""",
                depends_on=["text_description", "diagram_spec"],
                config=StepConfig(timeout=200.0),
                metadata={"type": "combination", "version": "1.0"},
            ),
        ]

        return PromptChain(
            steps=steps,
            name="ArchitectureDiagram",
            fail_fast=False,
        )

    @staticmethod
    def custom_chain(
        steps: List[PromptStep],
        name: Optional[str] = None,
        fail_fast: bool = True,
    ) -> PromptChain:
        """
        Create a custom prompt chain.

        Args:
            steps: List of PromptStep objects
            name: Optional name for the chain
            fail_fast: Whether to stop on first failure

        Returns:
            Custom PromptChain
        """
        return PromptChain(
            steps=steps,
            name=name or "CustomChain",
            fail_fast=fail_fast,
        )

    @staticmethod
    def get_available_chains() -> Dict[str, str]:
        """
        Get available chain types and their descriptions.

        Returns:
            Dictionary mapping chain type names to descriptions
        """
        return {
            "simple": "Single-step documentation generation",
            "enhanced": "Multi-step analysis, generation, and enhancement",
            "architecture": "Architecture documentation with diagram specifications",
            "multi_file": "Multi-file analysis with cross-file relationships",
            "codebase": "Comprehensive codebase analysis with synthesis",
        }

    @classmethod
    def create_chain(cls, chain_type: str, **kwargs) -> PromptChain:
        """
        Create a chain by type name.

        Args:
            chain_type: Type of chain to create
            **kwargs: Additional arguments for chain creation

        Returns:
            PromptChain instance

        Raises:
            ValueError: If chain_type is not recognized
        """
        if chain_type == "simple":
            return cls.simple_documentation_chain()
        elif chain_type == "enhanced":
            return cls.enhanced_documentation_chain()
        elif chain_type == "architecture":
            return cls.architecture_diagram_chain()
        elif chain_type == "multi_file":
            doc_type = kwargs.get("doc_type", "developer")
            project_type = kwargs.get("project_type", "auto")
            return cls.multi_file_analysis_chain(doc_type, project_type)
        elif chain_type == "codebase":
            doc_type = kwargs.get("doc_type", "developer")
            project_type = kwargs.get("project_type", "auto")
            return cls.codebase_analysis_chain(doc_type, project_type)
        elif chain_type == "custom":
            # Custom chains require steps to be provided
            steps = kwargs.get("steps")
            if not steps:
                raise ValueError("Custom chains require 'steps' parameter")
            return cls.custom_chain(steps, **kwargs)
        else:
            available = list(cls.get_available_chains().keys())
            raise ValueError(
                f"Unknown chain type '{chain_type}'. " f"Available types: {available}"
            )

    @staticmethod
    def multi_file_analysis_chain(
        doc_type: str = "developer", project_type: str = "auto"
    ) -> PromptChain:
        """
        Create a chain for multi-file analysis and documentation.

        Steps:
        1. Analyze the group of files and their relationships
        2. Identify cross-file dependencies and architecture
        3. Generate comprehensive documentation for the file group

        Args:
            doc_type: Type of documentation to generate (developer, user, both)
            project_type: Type of project for tailored analysis

        Returns:
            PromptChain for multi-file analysis and documentation
        """
        # Use new enhanced prompts based on documentation type
        if doc_type == "developer":
            analysis_prompt = """
You are an expert software architect analyzing multiple related files.
Generate comprehensive developer documentation with systems architecture focus.

**Analysis Level**: Module-level + Strategic Class-level
- Focus on module interactions and service boundaries
- Include only strategic/architectural classes, not implementation details
- Emphasize microservices patterns and deployment considerations

**Project Type**: {project_type}

**Files to Analyze**:
{files_content}

The documentation should include:

1. **System Purpose & Architecture**: What problem does this solve? Key architectural decisions and overall system design
2. **Module Interaction Analysis**: How do these modules/files interact and depend on each other? Service boundaries and data flow
3. **Key Class Relationships**: Core abstractions, design patterns, and critical dependency relationships
4. **Microservices Architecture Insights**: Service boundary identification, communication patterns, team ownership
5. **Development Guide**: Extension points, key patterns to follow, architecture constraints

**Guidelines**:
- Focus on cross-file relationships and dependencies
- Identify architectural patterns across multiple files
- Explain how components work together as a system
- Include specific examples of file interactions
- Consider microservices architecture and deployment patterns

Write comprehensive documentation analyzing these files together:"""

        elif doc_type == "user":
            analysis_prompt = """
You are an expert technical writer analyzing multiple application files.
Generate practical user documentation focusing on how to use this application.

**Analysis Instructions**:
- Focus on user-facing functionality across these files
- Identify command-line interfaces, configuration options, and usage patterns
- Provide practical examples of how to run and configure the application
- Include troubleshooting and operational guidance

**Files to Analyze**:
{files_content}

The documentation should include:

1. **Quick Start**: Primary use cases, installation steps, first successful run example
2. **Command Line Interface**: Available commands with examples, common usage patterns, configuration options
3. **Configuration Guide**: Environment variables, configuration file structure, common scenarios
4. **Operational Guide**: Monitoring, troubleshooting, performance considerations

**Guidelines**:
- Use command-line examples, not code examples
- Focus on practical usage and configuration
- Show how to install, configure, and operate the application
- Include troubleshooting for common issues

Write practical user documentation for this application:"""

        else:  # both
            analysis_prompt = """
You are an expert software architect and technical writer.
Generate comprehensive documentation for both developers and users.

**Analysis Level**: Module-level + Strategic Class-level for developers
**Project Type**: {project_type}

**Files to Analyze**:
{files_content}

Generate TWO sections:

## Developer Documentation
1. **System Purpose & Architecture**: Key architectural decisions and system design
2. **Module Interaction Analysis**: File interactions, service boundaries, data flow
3. **Key Class Relationships**: Core abstractions and design patterns
4. **Development Guide**: Extension points and architecture constraints

## User Documentation
1. **Quick Start**: Installation and first run
2. **Command Line Interface**: Commands and usage examples
3. **Configuration Guide**: Settings and configuration options
4. **Operational Guide**: Troubleshooting and operations

Write comprehensive documentation for both audiences:"""

        steps = [
            PromptStep(
                name="multi_file_documentation",
                prompt_template=analysis_prompt,
                config=StepConfig(timeout=360.0),
                metadata={
                    "type": "multi_file_documentation",
                    "version": "2.0",
                    "doc_type": doc_type,
                    "project_type": project_type,
                },
            ),
        ]

        return PromptChain(
            steps=steps,
            name=f"MultiFileAnalysis_{doc_type}",
            fail_fast=False,
        )

    @staticmethod
    def codebase_analysis_chain(
        doc_type: str = "developer", project_type: str = "auto"
    ) -> PromptChain:
        """
        Create a chain for comprehensive codebase analysis and documentation.

        For large codebases with multiple file groups, this chain:
        1. Analyzes individual groups
        2. Identifies cross-group relationships
        3. Synthesizes comprehensive overview
        4. Creates structured documentation

        Returns:
            PromptChain for codebase-level analysis
        """
        steps = [
            PromptStep(
                name="codebase_overview",
                prompt_template="""
Analyze this codebase structure and provide a high-level overview:

**Codebase Structure:**
- Total files: {total_files}
- Analysis groups: {groups}
- Primary directories: {primary_directories}

**Group Details:**
{group_summaries}

**Large Files (analyzed separately):**
{large_files}

Provide:
1. Overall purpose and architecture of this codebase
2. Main modules and their responsibilities
3. Key design patterns and architectural decisions
4. Technology stack and dependencies

Codebase Overview:""",
                config=StepConfig(timeout=300.0),
                metadata={"type": "codebase_overview", "version": "1.0"},
            ),
            PromptStep(
                name="cross_group_analysis",
                prompt_template="""
Based on the codebase overview:

{codebase_overview}

Analyze the relationships between different modules/groups:

**Group Details:**
{group_summaries}

Focus on:
1. How different modules interact with each other
2. Data flow between components
3. Shared interfaces and contracts
4. Dependencies and coupling patterns
5. Integration points and APIs

Cross-Group Analysis:""",
                depends_on=["codebase_overview"],
                config=StepConfig(timeout=360.0),
                metadata={"type": "cross_group_analysis", "version": "1.0"},
            ),
            PromptStep(
                name="architecture_synthesis",
                prompt_template="""
Create a comprehensive architectural analysis:

**Codebase Overview:** {codebase_overview}

**Cross-Group Analysis:** {cross_group_analysis}

**Detailed Group Information:**
{group_summaries}

Synthesize into:
1. **System Architecture**: High-level design and component relationships
2. **Module Structure**: How code is organized and why
3. **Key Abstractions**: Main concepts and design patterns
4. **Integration Patterns**: How components communicate
5. **Extensibility**: How the system can be extended
6. **Best Practices**: Coding patterns and conventions used

Architecture Synthesis:""",
                depends_on=["codebase_overview", "cross_group_analysis"],
                config=StepConfig(timeout=420.0),
                metadata={"type": "architecture_synthesis", "version": "1.0"},
            ),
            PromptStep(
                name="comprehensive_documentation",
                prompt_template="""
Create comprehensive documentation for this codebase:

**Overview:** {codebase_overview}

**Architecture:** {architecture_synthesis}

**Cross-Group Analysis:** {cross_group_analysis}

Generate structured documentation including:

# Codebase Documentation

## 1. Project Overview
[Brief description and purpose]

## 2. Architecture
[System design and component relationships]

## 3. Module Structure
[Organization and responsibilities]

## 4. Key Components
[Main classes, functions, and interfaces]

## 5. Integration Guide
[How components work together]

## 6. Development Guide
[Patterns, conventions, and best practices]

## 7. Extension Points
[How to extend the system]

Comprehensive Documentation:""",
                depends_on=[
                    "codebase_overview",
                    "cross_group_analysis",
                    "architecture_synthesis",
                ],
                config=StepConfig(timeout=480.0),
                metadata={"type": "comprehensive_documentation", "version": "1.0"},
            ),
        ]

        return PromptChain(
            steps=steps,
            name="CodebaseAnalysis",
            fail_fast=False,
        )
