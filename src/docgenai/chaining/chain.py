"""
Main prompt chain orchestrator for multi-step AI generation.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from .context import ChainContext
from .step import PromptStep

logger = logging.getLogger(__name__)


class PromptChain:
    """
    Orchestrates execution of multiple prompt steps in sequence.

    Manages dependencies between steps and provides error handling,
    retry logic, and execution monitoring.
    """

    def __init__(
        self,
        steps: List[PromptStep],
        name: Optional[str] = None,
        fail_fast: bool = True,
        max_parallel: int = 1,
    ):
        """
        Initialize a prompt chain.

        Args:
            steps: List of PromptStep objects to execute
            name: Optional name for this chain
            fail_fast: If True, stop execution on first failure
            max_parallel: Maximum number of parallel steps (future feature)
        """
        self.steps = steps
        self.name = name or f"Chain_{id(self)}"
        self.fail_fast = fail_fast
        self.max_parallel = max_parallel

        # Validate chain
        self._validate_chain()

    def _validate_chain(self) -> None:
        """Validate the chain configuration."""
        step_names = [step.name for step in self.steps]

        # Check for duplicate step names
        if len(step_names) != len(set(step_names)):
            duplicates = [name for name in step_names if step_names.count(name) > 1]
            raise ValueError(f"Duplicate step names: {duplicates}")

        # Check for invalid dependencies
        for step in self.steps:
            for dependency in step.depends_on:
                if dependency not in step_names:
                    raise ValueError(
                        f"Step '{step.name}' depends on unknown step " f"'{dependency}'"
                    )

        # Check for circular dependencies
        self._check_circular_dependencies()

    def _check_circular_dependencies(self) -> None:
        """Check for circular dependencies in the chain."""

        def has_cycle(step_name: str, visited: set, path: set) -> bool:
            if step_name in path:
                return True
            if step_name in visited:
                return False

            visited.add(step_name)
            path.add(step_name)

            # Find the step
            step = next((s for s in self.steps if s.name == step_name), None)
            if step:
                for dependency in step.depends_on:
                    if has_cycle(dependency, visited, path):
                        return True

            path.remove(step_name)
            return False

        visited = set()
        for step in self.steps:
            if step.name not in visited:
                if has_cycle(step.name, visited, set()):
                    raise ValueError(
                        f"Circular dependency detected involving step " f"'{step.name}'"
                    )

    def _get_execution_order(self) -> List[PromptStep]:
        """
        Determine the execution order based on dependencies.

        Returns:
            List of steps in execution order
        """
        executed = set()
        ordered_steps = []

        while len(ordered_steps) < len(self.steps):
            # Find steps that can be executed
            ready_steps = [
                step
                for step in self.steps
                if (
                    step.name not in executed
                    and all(dep in executed for dep in step.depends_on)
                )
            ]

            if not ready_steps:
                remaining = [
                    step.name for step in self.steps if step.name not in executed
                ]
                raise ValueError(
                    f"Cannot resolve dependencies for remaining steps: " f"{remaining}"
                )

            # Add the first ready step (could be improved for parallel exec)
            next_step = ready_steps[0]
            ordered_steps.append(next_step)
            executed.add(next_step.name)

        return ordered_steps

    def execute(
        self,
        model_fn: Callable[[str], str],
        initial_inputs: Optional[Dict[str, Any]] = None,
    ) -> ChainContext:
        """
        Execute the prompt chain.

        Args:
            model_fn: Function to call the AI model with a prompt
            initial_inputs: Initial input parameters for the chain

        Returns:
            ChainContext with all results and metadata
        """
        context = ChainContext(initial_inputs)
        context.set_metadata("chain_name", self.name)

        logger.info(f"🔗 Starting chain execution: {self.name}")
        logger.info(f"📋 Chain has {len(self.steps)} steps")

        try:
            # Get execution order
            ordered_steps = self._get_execution_order()
            context.set_metadata("execution_order", [s.name for s in ordered_steps])

            # Execute steps in order
            for i, step in enumerate(ordered_steps, 1):
                logger.info(f"🔄 Executing step {i}/{len(ordered_steps)}: {step.name}")
                context.current_step = step.name

                # Execute the step
                result = step.execute(context, model_fn)
                context.add_result(result)

                # Log result
                if result.error:
                    logger.error(f"❌ Step '{step.name}' failed: {result.error}")
                    if self.fail_fast:
                        logger.error("🛑 Stopping chain execution (fail_fast=True)")
                        break
                else:
                    logger.info(
                        f"✅ Step '{step.name}' completed in "
                        f"{result.execution_time:.2f}s"
                    )

        except Exception as e:
            logger.error(f"💥 Chain execution failed: {str(e)}")
            context.set_metadata("chain_error", str(e))

        finally:
            context.mark_complete()
            context.current_step = None

        # Log summary
        logger.info(f"🏁 Chain execution complete: {self.name}")
        logger.info(
            f"📊 Results: {context.success_count} successful, "
            f"{context.failure_count} failed, "
            f"{context.execution_time:.2f}s total"
        )

        return context

    def get_step(self, name: str) -> Optional[PromptStep]:
        """Get a step by name."""
        return next((step for step in self.steps if step.name == name), None)

    def add_step(self, step: PromptStep) -> None:
        """Add a step to the chain."""
        self.steps.append(step)
        self._validate_chain()  # Re-validate after adding

    def remove_step(self, name: str) -> bool:
        """Remove a step from the chain."""
        original_length = len(self.steps)
        self.steps = [step for step in self.steps if step.name != name]
        return len(self.steps) < original_length

    @property
    def step_names(self) -> List[str]:
        """Get list of all step names."""
        return [step.name for step in self.steps]

    def __repr__(self) -> str:
        """String representation of the chain."""
        return (
            f"PromptChain(name='{self.name}', "
            f"steps={len(self.steps)}, "
            f"step_names={self.step_names})"
        )
