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
        Get list of available pre-built chains.

        Returns:
            Dictionary mapping chain names to descriptions
        """
        return {
            "simple": "Single-step documentation generation (current behavior)",
            "enhanced": "Multi-step analysis, generation, and enhancement",
            "architecture": "Architecture documentation with diagram specifications",
            "custom": "User-defined custom chain configuration",
        }

    @classmethod
    def create_chain(cls, chain_type: str, **kwargs) -> PromptChain:
        """
        Create a chain by type name.

        Args:
            chain_type: Type of chain to create
            **kwargs: Additional arguments for custom chains

        Returns:
            PromptChain of the specified type
        """
        if chain_type == "simple":
            return cls.simple_documentation_chain()
        elif chain_type == "enhanced":
            return cls.enhanced_documentation_chain()
        elif chain_type == "architecture":
            return cls.architecture_diagram_chain()
        elif chain_type == "custom":
            return cls.custom_chain(**kwargs)
        else:
            available = list(cls.get_available_chains().keys())
            raise ValueError(
                f"Unknown chain type '{chain_type}'. " f"Available types: {available}"
            )
