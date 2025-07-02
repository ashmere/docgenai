"""
Tests for the prompt chaining system.
"""

import time
from unittest.mock import MagicMock, Mock

import pytest

from docgenai.chaining import (
    ChainBuilder,
    ChainContext,
    PromptChain,
    PromptStep,
    StepConfig,
    StepResult,
)


class TestChainContext:
    """Test ChainContext functionality."""

    def test_initialization(self):
        """Test context initialization."""
        inputs = {"code": "test code", "file_path": "test.py"}
        context = ChainContext(inputs)

        assert context.inputs == inputs
        assert context.results == {}
        assert context.metadata == {}
        assert context.start_time > 0
        assert context.end_time is None
        assert context.current_step is None

    def test_input_operations(self):
        """Test input get/set operations."""
        context = ChainContext()

        context.set_input("key", "value")
        assert context.get_input("key") == "value"
        assert context.get_input("missing", "default") == "default"

    def test_result_operations(self):
        """Test result operations."""
        context = ChainContext()

        result = StepResult(
            step_name="test_step", output="test output", execution_time=1.0
        )

        context.add_result(result)

        assert context.get_result("test_step") == result
        assert context.get_output("test_step") == "test output"
        assert context.has_result("test_step") is True
        assert context.has_result("missing_step") is False

    def test_failed_steps(self):
        """Test failed step tracking."""
        context = ChainContext()

        # Add successful result
        success_result = StepResult(step_name="success_step", output="success output")
        context.add_result(success_result)

        # Add failed result
        failed_result = StepResult(
            step_name="failed_step", output="", error="Test error"
        )
        context.add_result(failed_result)

        assert context.get_failed_steps() == ["failed_step"]
        assert context.success_count == 1
        assert context.failure_count == 1

    def test_completion_tracking(self):
        """Test completion tracking."""
        context = ChainContext()

        assert context.is_complete is False
        assert context.execution_time > 0  # Should be current time - start

        context.mark_complete()

        assert context.is_complete is True
        assert context.end_time is not None

    def test_serialization(self):
        """Test context serialization."""
        context = ChainContext({"input_key": "input_value"})
        context.set_metadata("meta_key", "meta_value")

        result = StepResult(
            step_name="test_step", output="test output", execution_time=1.5
        )
        context.add_result(result)
        context.mark_complete()

        data = context.to_dict()

        assert data["inputs"]["input_key"] == "input_value"
        assert data["metadata"]["meta_key"] == "meta_value"
        assert data["results"]["test_step"]["output"] == "test output"
        assert data["step_count"] == 1
        assert data["success_count"] == 1
        assert data["failure_count"] == 0


class TestPromptStep:
    """Test PromptStep functionality."""

    def test_initialization(self):
        """Test step initialization."""
        step = PromptStep(
            name="test_step",
            prompt_template="Test prompt: {code}",
            depends_on=["previous_step"],
            metadata={"type": "test"},
        )

        assert step.name == "test_step"
        assert step.prompt_template == "Test prompt: {code}"
        assert step.depends_on == ["previous_step"]
        assert step.metadata["type"] == "test"
        assert isinstance(step.config, StepConfig)

    def test_dependency_checking(self):
        """Test dependency checking."""
        step = PromptStep(
            name="dependent_step",
            prompt_template="Template",
            depends_on=["step1", "step2"],
        )

        context = ChainContext()

        # No dependencies satisfied
        assert step.can_execute(context) is False
        assert step.get_missing_dependencies(context) == ["step1", "step2"]

        # One dependency satisfied
        result1 = StepResult(step_name="step1", output="output1")
        context.add_result(result1)

        assert step.can_execute(context) is False
        assert step.get_missing_dependencies(context) == ["step2"]

        # All dependencies satisfied
        result2 = StepResult(step_name="step2", output="output2")
        context.add_result(result2)

        assert step.can_execute(context) is True
        assert step.get_missing_dependencies(context) == []

    def test_prompt_building(self):
        """Test prompt building with variables."""
        step = PromptStep(
            name="test_step",
            prompt_template="Code: {code}\nPrevious: {step1}\nFile: {file_path}",
            depends_on=["step1"],
        )

        context = ChainContext({"code": "test code", "file_path": "test.py"})
        result1 = StepResult(step_name="step1", output="previous output")
        context.add_result(result1)

        prompt = step.build_prompt(context)

        expected = "Code: test code\nPrevious: previous output\nFile: test.py"
        assert prompt == expected

    def test_prompt_building_missing_variable(self):
        """Test prompt building with missing variable."""
        step = PromptStep(
            name="test_step", prompt_template="Code: {code}\nMissing: {missing_var}"
        )

        context = ChainContext({"code": "test code"})

        with pytest.raises(ValueError, match="Missing variable"):
            step.build_prompt(context)

    def test_execution_success(self):
        """Test successful step execution."""
        step = PromptStep(name="test_step", prompt_template="Test prompt: {code}")

        context = ChainContext({"code": "test code"})

        # Mock model function
        mock_model = Mock(return_value="Generated output")

        result = step.execute(context, mock_model)

        assert result.step_name == "test_step"
        assert result.output == "Generated output"
        assert result.error is None
        assert result.execution_time > 0
        assert result.metadata["dependencies"] == []

        # Verify model was called with correct prompt
        mock_model.assert_called_once_with("Test prompt: test code")

    def test_execution_with_transform(self):
        """Test execution with transformation function."""

        def transform_fn(output, context):
            return f"Transformed: {output}"

        step = PromptStep(
            name="test_step",
            prompt_template="Test prompt: {code}",
            transform_fn=transform_fn,
        )

        context = ChainContext({"code": "test code"})
        mock_model = Mock(return_value="Original output")

        result = step.execute(context, mock_model)

        assert result.output == "Transformed: Original output"

    def test_execution_failure(self):
        """Test step execution failure."""
        step = PromptStep(name="test_step", prompt_template="Test prompt: {code}")

        context = ChainContext({"code": "test code"})

        # Mock model function that raises exception
        mock_model = Mock(side_effect=Exception("Model error"))

        result = step.execute(context, mock_model)

        assert result.step_name == "test_step"
        assert result.output == ""
        assert "Model error" in result.error
        assert result.execution_time > 0

    def test_execution_missing_dependencies(self):
        """Test execution with missing dependencies."""
        step = PromptStep(
            name="test_step", prompt_template="Test prompt", depends_on=["missing_step"]
        )

        context = ChainContext()
        mock_model = Mock()

        result = step.execute(context, mock_model)

        assert result.error is not None
        assert "Missing dependencies" in result.error
        mock_model.assert_not_called()


class TestPromptChain:
    """Test PromptChain functionality."""

    def test_initialization(self):
        """Test chain initialization."""
        step1 = PromptStep(name="step1", prompt_template="Template1")
        step2 = PromptStep(name="step2", prompt_template="Template2")

        chain = PromptChain(steps=[step1, step2], name="test_chain", fail_fast=False)

        assert chain.name == "test_chain"
        assert chain.fail_fast is False
        assert len(chain.steps) == 2
        assert chain.step_names == ["step1", "step2"]

    def test_duplicate_step_names(self):
        """Test validation of duplicate step names."""
        step1 = PromptStep(name="duplicate", prompt_template="Template1")
        step2 = PromptStep(name="duplicate", prompt_template="Template2")

        with pytest.raises(ValueError, match="Duplicate step names"):
            PromptChain(steps=[step1, step2])

    def test_invalid_dependencies(self):
        """Test validation of invalid dependencies."""
        step1 = PromptStep(name="step1", prompt_template="Template1")
        step2 = PromptStep(
            name="step2", prompt_template="Template2", depends_on=["nonexistent_step"]
        )

        with pytest.raises(ValueError, match="depends on unknown step"):
            PromptChain(steps=[step1, step2])

    def test_circular_dependencies(self):
        """Test detection of circular dependencies."""
        step1 = PromptStep(
            name="step1", prompt_template="Template1", depends_on=["step2"]
        )
        step2 = PromptStep(
            name="step2", prompt_template="Template2", depends_on=["step1"]
        )

        with pytest.raises(ValueError, match="Circular dependency"):
            PromptChain(steps=[step1, step2])

    def test_execution_order(self):
        """Test execution order determination."""
        step1 = PromptStep(name="step1", prompt_template="Template1")
        step2 = PromptStep(
            name="step2", prompt_template="Template2", depends_on=["step1"]
        )
        step3 = PromptStep(name="step3", prompt_template="Template3")

        chain = PromptChain(steps=[step2, step3, step1])  # Unordered

        ordered_steps = chain._get_execution_order()
        ordered_names = [step.name for step in ordered_steps]

        # step1 and step3 can be first (no dependencies)
        # step2 must come after step1
        assert ordered_names.index("step2") > ordered_names.index("step1")

    def test_successful_execution(self):
        """Test successful chain execution."""
        step1 = PromptStep(name="step1", prompt_template="First: {code}")
        step2 = PromptStep(
            name="step2", prompt_template="Second: {step1}", depends_on=["step1"]
        )

        chain = PromptChain(steps=[step1, step2])

        # Mock model function
        responses = {"First: test code": "Output 1", "Second: Output 1": "Output 2"}
        mock_model = Mock(side_effect=lambda prompt: responses[prompt])

        context = chain.execute(mock_model, {"code": "test code"})

        assert context.success_count == 2
        assert context.failure_count == 0
        assert context.get_output("step1") == "Output 1"
        assert context.get_output("step2") == "Output 2"
        assert context.is_complete is True

    def test_execution_with_failure_continue(self):
        """Test execution with failure and fail_fast=False."""
        step1 = PromptStep(name="step1", prompt_template="Template1")
        step2 = PromptStep(name="step2", prompt_template="Template2")

        chain = PromptChain(steps=[step1, step2], fail_fast=False)

        # Mock model that fails on first call
        mock_model = Mock()
        mock_model.side_effect = [Exception("Error"), "Success"]

        context = chain.execute(mock_model, {})

        assert context.success_count == 1
        assert context.failure_count == 1
        assert context.get_failed_steps() == ["step1"]
        assert context.get_output("step2") == "Success"

    def test_execution_with_failure_stop(self):
        """Test execution with failure and fail_fast=True."""
        step1 = PromptStep(name="step1", prompt_template="Template1")
        step2 = PromptStep(name="step2", prompt_template="Template2")

        chain = PromptChain(steps=[step1, step2], fail_fast=True)

        # Mock model that fails on first call
        mock_model = Mock()
        mock_model.side_effect = [Exception("Error"), "Success"]

        context = chain.execute(mock_model, {})

        assert context.success_count == 0
        assert context.failure_count == 1
        assert context.get_failed_steps() == ["step1"]
        assert context.get_output("step2") is None  # Should not execute

    def test_step_management(self):
        """Test adding and removing steps."""
        step1 = PromptStep(name="step1", prompt_template="Template1")
        chain = PromptChain(steps=[step1])

        # Test get_step
        assert chain.get_step("step1") == step1
        assert chain.get_step("nonexistent") is None

        # Test add_step
        step2 = PromptStep(name="step2", prompt_template="Template2")
        chain.add_step(step2)
        assert "step2" in chain.step_names

        # Test remove_step
        assert chain.remove_step("step1") is True
        assert chain.remove_step("nonexistent") is False
        assert "step1" not in chain.step_names


class TestChainBuilder:
    """Test ChainBuilder functionality."""

    def test_simple_documentation_chain(self):
        """Test simple documentation chain creation."""
        chain = ChainBuilder.simple_documentation_chain()

        assert chain.name == "SimpleDocumentation"
        assert len(chain.steps) == 1
        assert chain.steps[0].name == "documentation"
        assert "{code}" in chain.steps[0].prompt_template

    def test_enhanced_documentation_chain(self):
        """Test enhanced documentation chain creation."""
        chain = ChainBuilder.enhanced_documentation_chain()

        assert chain.name == "EnhancedDocumentation"
        assert len(chain.steps) == 3

        step_names = [step.name for step in chain.steps]
        assert "analyze" in step_names
        assert "documentation" in step_names
        assert "enhance" in step_names

        # Check dependencies
        doc_step = chain.get_step("documentation")
        assert "analyze" in doc_step.depends_on

        enhance_step = chain.get_step("enhance")
        assert "analyze" in enhance_step.depends_on
        assert "documentation" in enhance_step.depends_on

    def test_architecture_diagram_chain(self):
        """Test architecture diagram chain creation."""
        chain = ChainBuilder.architecture_diagram_chain()

        assert chain.name == "ArchitectureDiagram"
        assert len(chain.steps) == 4

        step_names = [step.name for step in chain.steps]
        expected_steps = [
            "architecture_analysis",
            "text_description",
            "diagram_spec",
            "combined_documentation",
        ]

        for expected in expected_steps:
            assert expected in step_names

    def test_custom_chain(self):
        """Test custom chain creation."""
        step1 = PromptStep(name="custom1", prompt_template="Template1")
        step2 = PromptStep(name="custom2", prompt_template="Template2")

        chain = ChainBuilder.custom_chain(
            steps=[step1, step2], name="CustomTest", fail_fast=False
        )

        assert chain.name == "CustomTest"
        assert chain.fail_fast is False
        assert len(chain.steps) == 2

    def test_get_available_chains(self):
        """Test getting available chain types."""
        available = ChainBuilder.get_available_chains()

        assert isinstance(available, dict)
        assert "simple" in available
        assert "enhanced" in available
        assert "architecture" in available
        assert "multi_file" in available
        assert "codebase" in available

    def test_create_chain_by_type(self):
        """Test creating chains by type name."""
        # Test valid types
        simple_chain = ChainBuilder.create_chain("simple")
        assert simple_chain.name == "SimpleDocumentation"

        enhanced_chain = ChainBuilder.create_chain("enhanced")
        assert enhanced_chain.name == "EnhancedDocumentation"

        arch_chain = ChainBuilder.create_chain("architecture")
        assert arch_chain.name == "ArchitectureDiagram"

        # Test invalid type
        with pytest.raises(ValueError, match="Unknown chain type"):
            ChainBuilder.create_chain("invalid_type")


class TestStepConfig:
    """Test StepConfig functionality."""

    def test_default_configuration(self):
        """Test default step configuration."""
        config = StepConfig()

        assert config.timeout == 300.0
        assert config.retry_count == 0
        assert config.retry_delay == 1.0
        assert config.required is True
        assert config.skip_on_failure is False

    def test_custom_configuration(self):
        """Test custom step configuration."""
        config = StepConfig(
            timeout=600.0,
            retry_count=3,
            retry_delay=2.0,
            required=False,
            skip_on_failure=True,
        )

        assert config.timeout == 600.0
        assert config.retry_count == 3
        assert config.retry_delay == 2.0
        assert config.required is False
        assert config.skip_on_failure is True


class TestIntegration:
    """Integration tests for the chaining system."""

    def test_end_to_end_simple_chain(self):
        """Test end-to-end execution of simple chain."""
        chain = ChainBuilder.simple_documentation_chain()

        mock_model = Mock(return_value="Generated documentation")
        initial_inputs = {
            "code": "def hello(): pass",
            "file_path": "test.py",
            "language": "python",
        }

        context = chain.execute(mock_model, initial_inputs)

        assert context.success_count == 1
        assert context.failure_count == 0
        assert context.get_output("documentation") == "Generated documentation"

    def test_end_to_end_enhanced_chain(self):
        """Test end-to-end execution of enhanced chain."""
        chain = ChainBuilder.enhanced_documentation_chain()

        # Mock model responses
        responses = {
            0: "Analysis output",  # analyze step
            1: "Documentation output",  # documentation step
            2: "Enhanced output",  # enhance step
        }
        call_count = 0

        def mock_model(prompt):
            nonlocal call_count
            response = responses[call_count]
            call_count += 1
            return response

        initial_inputs = {
            "code": "def hello(): pass",
            "file_path": "test.py",
            "language": "python",
        }

        context = chain.execute(mock_model, initial_inputs)

        assert context.success_count == 3
        assert context.failure_count == 0
        assert context.get_output("analyze") == "Analysis output"
        assert context.get_output("documentation") == "Documentation output"
        assert context.get_output("enhance") == "Enhanced output"
