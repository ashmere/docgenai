# Multi-File Documentation

**Files analyzed:** chain.py, __init__.py, step.py, context.py

---



### Module/Package Overview

The `src/docgenai/chaining` directory contains a system designed to facilitate multi-step AI generation by orchestrating a sequence of prompts. This system is intended to be used in a broader documentation generation context, where each step in the sequence builds upon the outputs of previous steps.

### Individual File Descriptions

#### `chain.py`

`chain.py` is the main file responsible for orchestrating the execution of multiple prompt steps in sequence. It manages dependencies between steps, provides error handling, retry logic, and execution monitoring.

- **Classes**:
  - `PromptChain`: Orchestrates execution of multiple prompt steps in sequence.
  - `ChainContext`: Manages the state and results of the chain.

#### `step.py`

`step.py` defines individual steps in a prompt chain. Each step can depend on outputs from previous steps and can transform or combine those outputs in various ways.

- **Classes**:
  - `PromptStep`: Individual step in a prompt chain.
  - `StepConfig`: Configuration for a prompt step.

#### `context.py`

`context.py` provides a context for managing state and results during prompt chain execution. It allows for the centralized storage and retrieval of results from individual chain steps, along with metadata about the overall execution.

- **Classes**:
  - `ChainContext`: Context for managing state and results during prompt chain execution.
  - `StepResult`: Result from a single chain step.

### Cross-File Relationships and Dependencies

1. **Dependencies Between Files**:
   - `chain.py` and `step.py` are closely related, as `chain.py` uses `step.py` classes like `PromptStep` in its implementation.
   - `chain.py` and `context.py` are also closely related, as `chain.py` uses `context.py` classes like `ChainContext` to manage the state and results of the chain.
   - `step.py` and `context.py` interact, with `step.py` using `context.py` to build prompts and check dependencies, and `context.py` storing results from `step.py` executions.

2. **Shared Data Structures and Interfaces**:
   - `StepConfig`, `PromptStep`, `ChainContext`, and `StepResult` are shared data structures. They are used across multiple files to define step configurations, individual steps, chain context management, and step results, respectively.
   - These data structures define interfaces for interacting with the chain and context, ensuring consistency and compatibility across different parts of the system.

### Architecture and Design Patterns

1. **Chain Orchestration**: The `PromptChain` class in `chain.py` is responsible for managing the sequence of `PromptStep` objects. It ensures that each step can only execute if its dependencies have been satisfied.
2. **Error Handling and Retry Logic**: The `PromptChain` and `PromptStep` classes include mechanisms for failing fast and retrying steps in case of errors.
3. **Context Management**: The `ChainContext` class in `context.py` acts as a container for the state and results of the chain, allowing for the sharing of information between steps.

### Usage Examples and Integration Points

To use the system, you would typically create a `PromptChain` object, add `PromptStep` objects to it, and then execute the chain by calling the `execute` method. The `PromptStep` objects can depend on the outputs of previous steps, and the system ensures that each step executes only after its dependencies are satisfied.

Here is an example of how to use the system:

```python
from docgenai.chaining import PromptChain, PromptStep, StepConfig

# Define steps
step1 = PromptStep(
    name="Step1",
    prompt_template="Generate a summary for the document.",
    depends_on=[]
)

step2 = PromptStep(
    name="Step2",
    prompt_template="Generate detailed content based on the summary from Step1.",
    depends_on=["Step1"]
)

# Create chain and add steps
chain = PromptChain(steps=[step1, step2])

# Execute chain
chain.execute(model_fn=your_model_fn)
```

### API Documentation

#### `PromptChain` Class

- **`**init**(self, steps: List[PromptStep], name: Optional[str] = None, fail_fast: bool = True, max_parallel: int = 1) -> None`**:
  - `steps`: List of `PromptStep` objects to execute.
  - `name`: Optional name for this chain.
  - `fail_fast`: If True, stop execution on first failure.
  - `max_parallel`: Maximum number of parallel steps (future feature).

- **`_validate_chain(self) -> None`**: Validate the chain configuration.
- **`_get_execution_order(self) -> List[PromptStep]`**: Determine the execution order based on dependencies.
- **`execute(self, model_fn: Callable[[str], str], initial_inputs: Optional[Dict[str, Any]] = None) -> ChainContext`**: Execute the prompt chain.
- **`get_step(self, name: str) -> Optional[PromptStep]`**: Get a step by name.
- **`add_step(self, step: PromptStep) -> None`**: Add a step to the chain.
- **`remove_step(self, name: str) -> bool`**: Remove a step from the chain.
- **`**repr**(self) -> str`**: String representation of the chain.

#### `PromptStep` Class

- **`**init**(self, name: str, prompt_template: str, depends_on: Optional[List[str]] = None, transform_fn: Optional[Callable[[str, ChainContext], str]] = None, config: Optional[StepConfig] = None, metadata: Optional[Dict[str, Any]] = None) -> None`**:
  - `name`: Unique name for this step.
  - `prompt_template`: Template string for the prompt (can use {variables}).
  - `depends_on`: List of step names this step depends on.
  - `transform_fn`: Optional function to transform the AI output.
  - `config`: Step configuration options.
  - `metadata`: Additional metadata for this step.

- **`can_execute(self, context: ChainContext) -> bool`**: Check if this step can be executed given the current context.
- **`build_prompt(self, context: ChainContext) -> str`**: Build the prompt for this step using the context.
- **`execute(self, context: ChainContext, model_fn: Callable[[str], str]) -> StepResult`**: Execute this step.
- **`**repr**(self) -> str`**: String representation of the step.

#### `ChainContext` Class

- **`**init**(self, initial_inputs: Optional[Dict[str, Any]] = None) -> None`**: Initialize chain context.
- **`set_input(self, key: str, value: Any) -> None`**: Set an input parameter.
- **`get_input(self, key: str, default: Any = None) -> Any`**: Get an input parameter.
- **`add_result(self, step_result: StepResult) -> None`**: Add a step result to the context.
- **`get_result(self, step_name: str) -> Optional[StepResult]`**: Get result from a specific step.
- **`get_output(self, step_name: str) -> Optional[str]`**: Get output from a specific step.
- **`has_result(self, step_name: str) -> bool`**: Check if a step has completed successfully.
- **`get_all_outputs(self) -> Dict[str, str]`**: Get all successful step outputs.
- **`get_failed_steps(self) -> List[str]`**: Get list of failed step names.
- **`set_metadata(self, key: str, value: Any) -> None`**: Set metadata about the chain execution.
- **`get_metadata(self, key: str, default: Any = None) -> Any`**: Get metadata about the chain execution.
- **`mark_complete(self) -> None`**: Mark the chain execution as complete.
- **`to_dict(self) -> Dict[str, Any]`**: Convert context to dictionary for serialization.

This documentation provides a comprehensive overview of the system, its components, and how to use them effectively in a multi-step AI generation context.
