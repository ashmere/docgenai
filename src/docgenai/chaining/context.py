"""
Chain context for managing state between prompt chain steps.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StepResult:
    """Result from a single chain step."""

    step_name: str
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class ChainContext:
    """
    Context for managing state and results during prompt chain execution.

    Provides a centralized way to store and retrieve results from individual
    chain steps, along with metadata about the overall execution.
    """

    def __init__(self, initial_inputs: Optional[Dict[str, Any]] = None):
        """
        Initialize chain context.

        Args:
            initial_inputs: Initial input parameters for the chain
        """
        self.inputs = initial_inputs or {}
        self.results: Dict[str, StepResult] = {}
        self.metadata: Dict[str, Any] = {}
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.current_step: Optional[str] = None

    def set_input(self, key: str, value: Any) -> None:
        """Set an input parameter."""
        self.inputs[key] = value

    def get_input(self, key: str, default: Any = None) -> Any:
        """Get an input parameter."""
        return self.inputs.get(key, default)

    def add_result(self, step_result: StepResult) -> None:
        """Add a step result to the context."""
        self.results[step_result.step_name] = step_result

    def get_result(self, step_name: str) -> Optional[StepResult]:
        """Get result from a specific step."""
        return self.results.get(step_name)

    def get_output(self, step_name: str) -> Optional[str]:
        """Get output from a specific step."""
        result = self.get_result(step_name)
        return result.output if result else None

    def has_result(self, step_name: str) -> bool:
        """Check if a step has completed successfully."""
        result = self.get_result(step_name)
        return result is not None and result.error is None

    def get_all_outputs(self) -> Dict[str, str]:
        """Get all successful step outputs."""
        return {
            name: result.output
            for name, result in self.results.items()
            if result.error is None
        }

    def get_failed_steps(self) -> List[str]:
        """Get list of failed step names."""
        return [
            name for name, result in self.results.items() if result.error is not None
        ]

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata about the chain execution."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata about the chain execution."""
        return self.metadata.get(key, default)

    def mark_complete(self) -> None:
        """Mark the chain execution as complete."""
        self.end_time = time.time()

    @property
    def execution_time(self) -> float:
        """Total execution time for the chain."""
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def is_complete(self) -> bool:
        """Check if the chain execution is complete."""
        return self.end_time is not None

    @property
    def step_count(self) -> int:
        """Number of completed steps."""
        return len(self.results)

    @property
    def success_count(self) -> int:
        """Number of successful steps."""
        return len([r for r in self.results.values() if r.error is None])

    @property
    def failure_count(self) -> int:
        """Number of failed steps."""
        return len([r for r in self.results.values() if r.error is not None])

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "inputs": self.inputs,
            "results": {
                name: {
                    "step_name": result.step_name,
                    "output": result.output,
                    "metadata": result.metadata,
                    "execution_time": result.execution_time,
                    "error": result.error,
                    "timestamp": result.timestamp,
                }
                for name, result in self.results.items()
            },
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "step_count": self.step_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
        }
