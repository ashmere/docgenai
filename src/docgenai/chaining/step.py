"""
Individual step in a prompt chain.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from .context import ChainContext, StepResult


@dataclass
class StepConfig:
    """Configuration for a prompt step."""

    timeout: float = 300.0  # 5 minutes default
    retry_count: int = 0
    retry_delay: float = 1.0
    required: bool = True
    skip_on_failure: bool = False


class PromptStep:
    """
    Individual step in a prompt chain.

    Each step can depend on outputs from previous steps and can transform
    or combine those outputs in various ways.
    """

    def __init__(
        self,
        name: str,
        prompt_template: str,
        depends_on: Optional[List[str]] = None,
        transform_fn: Optional[Callable[[str, ChainContext], str]] = None,
        config: Optional[StepConfig] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a prompt step.

        Args:
            name: Unique name for this step
            prompt_template: Template string for the prompt (can use {variables})
            depends_on: List of step names this step depends on
            transform_fn: Optional function to transform the AI output
            config: Step configuration options
            metadata: Additional metadata for this step
        """
        self.name = name
        self.prompt_template = prompt_template
        self.depends_on = depends_on or []
        self.transform_fn = transform_fn
        self.config = config or StepConfig()
        self.metadata = metadata or {}

    def can_execute(self, context: ChainContext) -> bool:
        """
        Check if this step can be executed given the current context.

        Args:
            context: Current chain context

        Returns:
            True if all dependencies are satisfied
        """
        for dependency in self.depends_on:
            if not context.has_result(dependency):
                return False
        return True

    def get_missing_dependencies(self, context: ChainContext) -> List[str]:
        """
        Get list of missing dependencies.

        Args:
            context: Current chain context

        Returns:
            List of dependency names that are not satisfied
        """
        return [dep for dep in self.depends_on if not context.has_result(dep)]

    def build_prompt(self, context: ChainContext) -> str:
        """
        Build the prompt for this step using the context.

        Args:
            context: Current chain context

        Returns:
            Formatted prompt string
        """
        # Collect variables for template formatting
        variables = {}

        # Add initial inputs
        variables.update(context.inputs)

        # Add outputs from dependent steps
        for dependency in self.depends_on:
            output = context.get_output(dependency)
            if output is not None:
                variables[dependency] = output
                variables[f"{dependency}_output"] = output

        # Add all outputs with prefixed names
        all_outputs = context.get_all_outputs()
        for step_name, output in all_outputs.items():
            variables[f"step_{step_name}"] = output

        # Format the template
        try:
            return self.prompt_template.format(**variables)
        except KeyError as e:
            raise ValueError(
                f"Step '{self.name}': Missing variable {e} in prompt template. "
                f"Available variables: {list(variables.keys())}"
            )

    def execute(
        self, context: ChainContext, model_fn: Callable[[str], str]
    ) -> StepResult:
        """
        Execute this step.

        Args:
            context: Current chain context
            model_fn: Function to call the AI model

        Returns:
            StepResult with the output and metadata
        """
        start_time = time.time()

        try:
            # Check dependencies
            if not self.can_execute(context):
                missing = self.get_missing_dependencies(context)
                raise ValueError(f"Step '{self.name}': Missing dependencies: {missing}")

            # Build prompt
            prompt = self.build_prompt(context)

            # Execute with retries
            last_error = None
            for attempt in range(self.config.retry_count + 1):
                try:
                    # Call the model
                    raw_output = model_fn(prompt)

                    # Apply transformation if provided
                    if self.transform_fn:
                        output = self.transform_fn(raw_output, context)
                    else:
                        output = raw_output

                    # Success
                    execution_time = time.time() - start_time
                    return StepResult(
                        step_name=self.name,
                        output=output,
                        metadata={
                            **self.metadata,
                            "prompt_length": len(prompt),
                            "output_length": len(output),
                            "attempt": attempt + 1,
                            "dependencies": self.depends_on,
                        },
                        execution_time=execution_time,
                    )

                except Exception as e:
                    last_error = e
                    if attempt < self.config.retry_count:
                        time.sleep(self.config.retry_delay)
                        continue
                    else:
                        raise

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Step '{self.name}' failed: {str(e)}"

            return StepResult(
                step_name=self.name,
                output="",
                metadata={
                    **self.metadata,
                    "dependencies": self.depends_on,
                    "error_type": type(e).__name__,
                },
                execution_time=execution_time,
                error=error_msg,
            )

    def __repr__(self) -> str:
        """String representation of the step."""
        deps = f", depends_on={self.depends_on}" if self.depends_on else ""
        return f"PromptStep(name='{self.name}'{deps})"
