"""
AI Model abstraction layer for DocGenAI.

This module provides platform-aware model selection:
- macOS: Uses MLX-optimized DeepSeek-Coder-V2-Lite-Instruct-8bit model
- Other platforms: Uses standard DeepSeek-Coder-V2-Lite-Instruct

The models are designed to generate comprehensive documentation
for codebases with focus on clarity and architectural understanding.
"""

import hashlib
import logging
import os
import platform
import sys
import time
import warnings
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

# Suppress MLX deprecation warnings for cleaner output
warnings.filterwarnings("ignore", message=".*mx.metal.* is deprecated.*")

logger = logging.getLogger(__name__)


@contextmanager
def suppress_stderr():
    """Context manager to temporarily suppress stderr output."""
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


class AIModel(ABC):
    """Abstract base class for AI models used in documentation generation."""

    @abstractmethod
    def generate_documentation(self, code: str, file_path: str, **kwargs) -> str:
        """Generate documentation for the given code."""
        pass

    @abstractmethod
    def generate_architecture_description(
        self, code: str, file_path: str, **kwargs
    ) -> str:
        """Generate architecture description for the given code."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and ready to use."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass


class DeepSeekCoderModel(AIModel):
    """
    DeepSeek-Coder-V2-Lite model implementation with platform detection.

    - macOS: Uses mlx-lm with DeepSeek-Coder-V2-Lite-Instruct-8bit
    - Linux/Windows: Uses transformers with DeepSeek-Coder-V2-Lite-Instruct
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize DeepSeek-Coder model with platform detection."""
        self.config = config or {}
        self.platform = platform.system()
        self.model = None
        self.tokenizer = None
        self.is_mac = self.platform == "Darwin"

        # Get model configuration
        model_config = self.config.get("model", {})

        # Model paths based on platform and config
        if self.is_mac:
            self.model_path = model_config.get(
                "mlx_model", "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit"
            )
            self.backend = "mlx"
        else:
            self.model_path = model_config.get(
                "transformers_model", "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
            )
            self.backend = "transformers"

        # Generation parameters from config
        self.temperature = model_config.get("temperature", 0.7)
        self.max_tokens = model_config.get("max_tokens", 2048)
        self.top_p = model_config.get("top_p", 0.8)
        self.top_k = model_config.get("top_k", 50)
        self.do_sample = model_config.get("do_sample", True)

        # Hardware optimization settings
        self.device_map = model_config.get("device_map", "auto")
        self.torch_dtype = model_config.get("torch_dtype", "auto")
        self.trust_remote_code = model_config.get("trust_remote_code", True)
        self.quantization = model_config.get("quantization", "4bit")

        logger.info(f"🖥️  Platform detected: {self.platform}")
        logger.info(f"🤖 Model backend: {self.backend}")
        logger.info(f"📍 Model path: {self.model_path}")

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the model based on platform."""
        logger.info("🔧 Initializing DeepSeek-Coder model...")
        start_time = time.time()

        try:
            if self.is_mac:
                self._initialize_mlx_model()
            else:
                self._initialize_transformers_model()

            elapsed = time.time() - start_time
            logger.info(
                f"🎉 Model initialization complete! "
                f"Total time: {elapsed:.2f} seconds"
            )

        except Exception as e:
            logger.error(f"❌ Model initialization failed: {str(e)}")
            raise

    def _initialize_mlx_model(self):
        """Initialize MLX model for macOS."""
        logger.info("📥 Step 1/3: Loading MLX model and tokenizer...")

        try:
            from mlx_lm import generate, load

            self.mlx_generate = generate

            # Load model and tokenizer
            logger.info(f"📦 Loading {self.model_path}...")
            self.model, self.tokenizer = load(self.model_path)
            logger.info("✅ MLX model loaded successfully")

        except ImportError as e:
            logger.error("❌ mlx-lm not available. Install with: pip install mlx-lm")
            raise ImportError(
                "mlx-lm is required for macOS. " "Install with: pip install mlx-lm"
            ) from e
        except Exception as e:
            logger.error(f"❌ Failed to load MLX model: {str(e)}")
            raise

    def _initialize_transformers_model(self):
        """Initialize transformers model for non-macOS platforms."""
        logger.info("📥 Step 1/4: Loading transformers model...")

        try:
            import torch
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                BitsAndBytesConfig,
            )

            # Set up quantization config if requested
            quantization_config = None
            if self.quantization == "4bit":
                logger.info("⚙️  Setting up 4-bit quantization...")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
            elif self.quantization == "8bit":
                logger.info("⚙️  Setting up 8-bit quantization...")
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                )

            # Load tokenizer
            logger.info("📝 Step 2/4: Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, trust_remote_code=self.trust_remote_code
            )
            logger.info("✅ Tokenizer loaded")

            # Load model
            logger.info("🧠 Step 3/4: Loading model...")

            # Determine torch dtype
            if self.torch_dtype == "auto":
                torch_dtype = (
                    torch.float16 if torch.cuda.is_available() else torch.float32
                )
            else:
                torch_dtype = getattr(torch, self.torch_dtype, torch.float32)

            model_kwargs = {
                "trust_remote_code": self.trust_remote_code,
                "torch_dtype": torch_dtype,
            }

            # Add quantization config if specified
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = self.device_map
            elif torch.cuda.is_available():
                model_kwargs["device_map"] = self.device_map

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path, **model_kwargs
            )
            logger.info("✅ Model loaded")

            # Set up generation config
            logger.info("⚙️  Step 4/4: Configuring generation parameters...")
            self.generation_config = {
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "do_sample": self.do_sample,
                "pad_token_id": self.tokenizer.eos_token_id,
            }
            logger.info("✅ Generation config set")

        except Exception as e:
            logger.error(f"❌ Failed to load transformers model: {str(e)}")
            raise

    def _generate_with_mlx(self, prompt: str, max_tokens: int = None) -> str:
        """Generate text using MLX backend."""
        try:
            from mlx_lm import sample_utils

            max_tokens = max_tokens or self.max_tokens

            # Create sampler using make_sampler function
            sampler = sample_utils.make_sampler(
                temp=self.temperature,
                top_p=self.top_p,
                min_p=0.0,
                top_k=self.top_k if hasattr(self, "top_k") else -1,
            )

            # Suppress MLX deprecation warnings during generation
            with suppress_stderr():
                response = self.mlx_generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    sampler=sampler,
                )
            return response
        except Exception as e:
            logger.error(f"❌ MLX generation failed: {str(e)}")
            raise

    def _generate_with_transformers(self, prompt: str, max_tokens: int = None) -> str:
        """Generate text using transformers backend."""
        try:
            import torch

            # Apply chat template for instruction-tuned model
            messages = [{"role": "user", "content": prompt}]

            # Use the tokenizer's chat template
            if hasattr(self.tokenizer, "apply_chat_template"):
                formatted_prompt = self.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            else:
                # Fallback to simple format
                formatted_prompt = f"User: {prompt}\n\nAssistant:"

            inputs = self.tokenizer.encode(formatted_prompt, return_tensors="pt")
            if torch.cuda.is_available() and hasattr(self.model, "device"):
                inputs = inputs.to(self.model.device)

            # Update generation config with any overrides
            gen_config = self.generation_config.copy()
            if max_tokens:
                gen_config["max_new_tokens"] = max_tokens

            with torch.no_grad():
                outputs = self.model.generate(inputs, **gen_config)

            # Decode only the new tokens
            response = self.tokenizer.decode(
                outputs[0][len(inputs[0]) :], skip_special_tokens=True
            )
            return response.strip()

        except Exception as e:
            logger.error(f"❌ Transformers generation failed: {str(e)}")
            raise

    def _generate_text(self, prompt: str, max_tokens: int = None) -> str:
        """Generate text using appropriate backend."""
        logger.info("🔄 Running model inference...")
        start_time = time.time()

        try:
            if self.is_mac:
                response = self._generate_with_mlx(prompt, max_tokens)
            else:
                response = self._generate_with_transformers(prompt, max_tokens)

            elapsed = time.time() - start_time
            logger.info(f"✅ Generation complete in {elapsed:.2f} seconds")

            return response

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ Generation failed after {elapsed:.2f} seconds: {str(e)}")
            raise

    def generate_documentation(self, code: str, file_path: str, **kwargs) -> str:
        """Generate comprehensive documentation for the given code."""
        logger.info(f"📝 Generating documentation for {file_path}")

        # Detect programming language
        file_extension = Path(file_path).suffix.lower()
        language = self._detect_language(file_extension)

        # Create documentation prompt
        prompt = f"""You are an expert software developer and technical writer. Generate comprehensive, clear, and well-structured documentation for the following {language} code.

The documentation should include:

1. **Overview**: Brief description of what the code does
2. **Key Components**: Main classes, functions, and their purposes
3. **Architecture**: How the components work together
4. **Usage Examples**: Practical examples of how to use the code
5. **Dependencies**: Any external libraries or modules used
6. **Configuration**: Any configuration options or environment variables
7. **Error Handling**: How errors are handled and common issues
8. **Performance Considerations**: Any performance notes or optimizations

Please write the documentation in clear, professional Markdown format. Use appropriate code blocks, headers, and formatting.

**File Path**: `{file_path}`

**Code**:
```{language}
{code}
```

**Documentation**:"""

        return self._generate_text(prompt)

    def generate_architecture_description(
        self, code: str, file_path: str, **kwargs
    ) -> str:
        """Generate architectural analysis for the given code."""
        logger.info(f"🏗️  Generating architecture description for {file_path}")

        file_extension = Path(file_path).suffix.lower()
        language = self._detect_language(file_extension)

        prompt = f"""You are a software architect analyzing code structure. Provide a detailed architectural analysis of the following {language} code.

Focus on:

1. **Architectural Patterns**: Design patterns used (MVC, Observer, Factory, etc.)
2. **Code Organization**: How the code is structured and organized
3. **Data Flow**: How data moves through the system
4. **Dependencies**: Internal and external dependencies
5. **Interfaces**: Public APIs and interfaces exposed
6. **Extensibility**: How the code can be extended or modified
7. **Design Principles**: SOLID principles, separation of concerns, etc.
8. **Potential Improvements**: Suggestions for architectural improvements

**File Path**: `{file_path}`

**Code**:
```{language}
{code}
```

**Architecture Analysis**:"""

        return self._generate_text(prompt)

    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
        }
        return language_map.get(file_extension.lower(), "text")

    def is_available(self) -> bool:
        """Check if the model is available and ready to use."""
        return self.model is not None and self.tokenizer is not None

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "model_path": self.model_path,
            "backend": self.backend,
            "platform": self.platform,
            "is_mac": self.is_mac,
            "available": self.is_available(),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "quantization": self.quantization if not self.is_mac else "8bit (MLX)",
        }


def create_model(config: Optional[Dict[str, Any]] = None) -> AIModel:
    """
    Create an appropriate AI model instance based on configuration.

    Args:
        config: Configuration dictionary

    Returns:
        AIModel instance (DeepSeekCoderModel)
    """
    logger.info("🏭 Creating AI model instance...")

    try:
        model = DeepSeekCoderModel(config)
        logger.info(
            f"✅ Created {model.__class__.__name__} with {model.backend} backend"
        )
        return model
    except Exception as e:
        logger.error(f"❌ Failed to create model: {str(e)}")
        raise


# Backward compatibility aliases
class DeepSeekV3Model(DeepSeekCoderModel):
    """Backward compatibility alias for DeepSeekCoderModel."""

    pass


class MMaDAModel(DeepSeekCoderModel):
    """Backward compatibility wrapper for old MMaDA model usage."""

    def __init__(self, model_name: str = None, **kwargs):
        logger.warning("⚠️  MMaDAModel is deprecated. Use DeepSeekCoderModel instead.")
        super().__init__(**kwargs)
