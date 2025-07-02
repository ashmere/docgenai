# Group 2 Documentation

**Files:** chain.py, __init__.py, step.py, context.py

---



### Module/Package Overview

The `src/docgenai/chaining` directory contains files designed to facilitate multi-step AI generation by orchestrating a sequence of prompts. This system is intended for use in applications where complex documentation or content generation tasks require multiple steps, each dependent on the outputs of previous steps.

### Individual File Descriptions

#### `chain.py`

This file contains the `PromptChain` class, which acts as the main orchestrator for executing multiple `PromptStep` objects in sequence. It manages dependencies between steps, provides error handling, retry logic, and execution monitoring.

#### `step.py`

The `PromptStep` class in this file represents individual steps in the chain, each with its own prompt template and optional transformation function. It includes methods to check dependencies, build prompts, and execute the step.

#### `context.py`

The `ChainContext` class in this file provides a centralized store for inputs, outputs, and metadata related to the chain execution. It includes methods to manage inputs, outputs, and metadata, and to mark the chain as complete.

#### `**init**.py`

This file serves as a container for the `PromptChain`, `PromptStep`, `ChainContext`, and `StepConfig` classes, making them available for import as part of the `docgenai.chaining` module.

### Cross-File Relationships and Dependencies

- `chain.py` depends on `step.py` for the `PromptStep` class and `context.py` for the `ChainContext` class.
- `step.py` depends on `context.py` for access to the chain's context during execution.
- `context.py` is used by `chain.py` to manage the state and results of the chain execution.

### Architecture and Design Patterns

The system follows a modular design, with each file (`chain.py`, `step.py`, `context.py`, and `**init**.py`) serving a specific purpose while working together to achieve the overall goal. The `PromptChain` class in `chain.py` acts as the main orchestrator, managing the sequence of `PromptStep` executions and handling dependencies between steps.
The `PromptStep` class in `step.py` represents individual steps in the chain, each with its own prompt template and optional transformation function. The `ChainContext` class in `context.py` provides a centralized store for inputs, outputs, and metadata related to the chain execution.

### Usage Examples and Integration Points

To use the system, you would typically create a `PromptChain` object, add `PromptStep` objects to it, and then execute the chain using a model function. Here's a simple example:

```python
from docgenai.chaining import PromptChain, PromptStep

# Define steps
step1 = PromptStep(
    name="Step1",
    prompt_template="What is the capital of {country}?",
    depends_on=[]
)

step2 = PromptStep(
    name="Step2",
    prompt_template="What is the population of {city}?",
    depends_on=["Step1"]
)

# Create chain and add steps
chain = PromptChain(steps=[step1, step2])

# Define a model function (mock for example)
def model_fn(prompt: str) -> str:
    # Mock implementation: just return the prompt
    return prompt

# Execute the chain
context = chain.execute(model_fn, initial_inputs={"country": "France"})

# Output results
print(context.get_output("Step1"))  # Output: "The capital of France is Paris."
print(context.get_output("Step2"))  # Output: "The population of Paris is 2,140,526."
```

### API Documentation

#### `PromptChain` Class

- **`**init**(self, steps: List[PromptStep], name: Optional[str] = None, fail_fast: bool = True, max_parallel: int = 1) -> None`**: Initializes a prompt chain with the given steps, name, fail-fast behavior, and maximum parallel steps.
- **`_validate_chain(self) -> None`**: Validates the chain configuration by checking for duplicate step names and invalid dependencies.
- **`_check_circular_dependencies(self) -> None`**: Checks for circular dependencies in the chain.
- **`_get_execution_order(self) -> List[PromptStep]`**: Determines the execution order based on dependencies.
- **`execute(self, model_fn: Callable[[str], str], initial_inputs: Optional[Dict[str, Any]] = None) -> ChainContext`**: Executes the chain using the provided model function and initial inputs.
- **`get_step(self, name: str) -> Optional[PromptStep]`**: Gets a step by name.
- **`add_step(self, step: PromptStep) -> None`**: Adds a step to the chain.
- **`remove_step(self, name: str) -> bool`**: Removes a step from the chain by name.
- **`step_names(self) -> List[str]`**: Gets a list of all step names.

#### `PromptStep` Class

- **`**init**(self, name: str, prompt_template: str, depends_on: Optional[List[str]] = None, transform_fn: Optional[Callable[[str, ChainContext], str]] = None, config: Optional[StepConfig] = None, metadata: Optional[Dict[str, Any]] = None) -> None`**: Initializes a prompt step with the given parameters.
- **`can_execute(self, context: ChainContext) -> bool`**: Checks if this step can be executed given the current context.
- **`get_missing_dependencies(self, context: ChainContext) -> List[str]`**: Gets list of missing dependencies.
- **`build_prompt(self, context: ChainContext) -> str`**: Builds the prompt for this step using the context.
- **`execute(self, context: ChainContext, model_fn: Callable[[str], str]) -> StepResult`**: Executes this step.

#### `ChainContext` Class

- **`**init**(self, initial_inputs: Optional[Dict[str, Any]] = None) -> None`**: Initializes the chain context with initial inputs.
- **`set_input(self, key: str, value: Any) -> None`**: Sets an input parameter.
- **`get_input(self, key: str, default: Any = None) -> Any`**: Gets an input parameter.
- **`add_result(self, step_result: StepResult) -> None`**: Adds a step result to the context.
- **`get_result(self, step_name: str) -> Optional[StepResult]`**: Gets result from a specific step.
- **`get_output(self, step_name: str) -> Optional[str]`**: Gets output from a specific step.
- **`has_result(self, step_name: str) -> bool`**: Checks if a step has completed successfully.
- **`get_all_outputs(self) -> Dict[str, str]`**: Gets all successful step outputs.
- **`get_failed_steps(self) -> List[str]`**: Gets list of failed step names.
- **`set_metadata(self, key: str, value: Any) -> None`**: Sets metadata about the chain execution.
- **`get_metadata(self, key: str, default: Any = None) -> Any`**: Gets metadata about the chain execution.
- **`mark_complete(self) -> None`**: Marks the chain execution as complete.
- **`execution_time(self) -> float`**: Total execution time for the chain.
- **`is_complete(self) -> bool`**: Checks if the chain execution is complete.
- **`step_count(self) -> int`**: Number of completed steps.
- **`success_count(self) -> int`**: Number of successful steps.
- **`failure_count(self) -> int`**: Number of failed steps.
- **`to_dict(self) -> Dict[str, Any]`**: Converts context to dictionary for serialization.

#### `StepConfig` Class

- **`**init**(self, timeout: float = 300.0, retry_count: int = 0, retry_delay: float = 1.0, required: bool = True, skip_on_failure: bool = False) -> None`**: Initializes the step configuration with the given parameters.
