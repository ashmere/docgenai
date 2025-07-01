"""
Model implementations for DocGenAI.

This module provides model classes for different backends (MLX and Transformers)
with automatic platform detection and optimized configurations.
"""

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

    @staticmethod
    def _get_platform_info():
        """Get platform information for model selection."""
        machine = platform.machine()

        # Check if MLX is available (for Apple Silicon, even in Docker)
        mlx_available = False
        try:
            import mlx.core  # noqa: F401

            mlx_available = True
        except ImportError:
            mlx_available = False

        # Platform selection logic:
        # 1. If MLX is available and we're on ARM64, use MLX
        # 2. Otherwise, use transformers
        if mlx_available and machine in ["arm64", "aarch64"]:
            return "mlx"
        else:
            return "transformers"


class DeepSeekCoderModel(AIModel):
    """
    DeepSeek-Coder-V2-Lite model implementation with platform detection.

    - macOS: Uses mlx-lm with model specified in config (mlx_model)
    - Linux/Windows: Uses transformers with model specified in config (transformers_model)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize DeepSeek-Coder model with platform detection."""
        self.config = config or {}
        self.platform = platform.system()
        self.model = None
        self.tokenizer = None
        self.is_mac = self.platform == "Darwin"

        # Initialize prompt manager
        from .prompts import PromptManager

        self.prompt_manager = PromptManager()

        # Get model configuration
        model_config = self.config.get("model", {})

        # Model paths based on platform and config
        if self.is_mac:
            self.model_path = model_config.get("mlx_model")
            self.backend = "mlx"
            if not self.model_path:
                raise ValueError(
                    "mlx_model must be specified in configuration for macOS"
                )
        else:
            self.model_path = model_config.get("transformers_model")
            self.backend = "transformers"
            if not self.model_path:
                raise ValueError(
                    "transformers_model must be specified in configuration "
                    "for Linux/Windows"
                )

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

        # Offline mode settings
        self.offline_mode = model_config.get("offline_mode", True)
        self.check_for_updates = model_config.get("check_for_updates", False)
        self.force_download = model_config.get("force_download", False)
        self.local_files_only = model_config.get("local_files_only", True)

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

            # Load model and tokenizer with offline settings
            logger.info(f"📦 Loading {self.model_path}...")

            # Configure download behavior for MLX
            load_kwargs = {}
            if self.offline_mode and not self.force_download:
                # For MLX, we'll try to load locally first
                logger.info("📴 Offline mode: attempting to use cached model")
            elif self.force_download:
                logger.info("⬇️  Force download: re-downloading model")

            self.model, self.tokenizer = load(self.model_path, **load_kwargs)
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
            )

            # Check if this is an AWQ model (already quantized)
            is_awq_model = "awq" in self.model_path.lower()

            # Configure download behavior
            load_kwargs = {
                "torch_dtype": torch.float16,
                "device_map": "auto",
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }

            # Add offline mode parameters
            if self.offline_mode and not self.force_download:
                load_kwargs["local_files_only"] = True
                logger.info("📴 Offline mode: using cached models only")
            elif self.force_download:
                load_kwargs["local_files_only"] = False
                load_kwargs["force_download"] = True
                logger.info("⬇️  Force download: re-downloading model")
            else:
                load_kwargs["local_files_only"] = False
                if self.check_for_updates:
                    logger.info("🔄 Checking for model updates")
                else:
                    logger.info("🌐 Online mode: may download if not cached")

            if is_awq_model:
                logger.info(
                    "⚙️  Detected AWQ model - loading without additional quantization"
                )
                # AWQ models are already quantized, load them directly
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path, **load_kwargs
                )
            else:
                # For non-AWQ models, use 4-bit quantization if requested
                logger.info(f"⚙️  Setting up {self.quantization} quantization...")

                if self.quantization == "4bit":
                    load_kwargs["load_in_4bit"] = True
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path, **load_kwargs
                    )
                elif self.quantization == "8bit":
                    load_kwargs["load_in_8bit"] = True
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path, **load_kwargs
                    )
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path, **load_kwargs
                    )

            logger.info("📝 Step 2/4: Loading tokenizer...")

            # Configure tokenizer loading with same offline settings
            tokenizer_kwargs = {
                "trust_remote_code": True,
            }

            if self.offline_mode and not self.force_download:
                tokenizer_kwargs["local_files_only"] = True
            elif self.force_download:
                tokenizer_kwargs["local_files_only"] = False
                tokenizer_kwargs["force_download"] = True
            else:
                tokenizer_kwargs["local_files_only"] = False

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, **tokenizer_kwargs
            )

            # Ensure tokenizer has pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.info("✅ Model and tokenizer loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load transformers model: {e}")
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

        # Build prompt using prompt manager
        prompt = self.prompt_manager.build_documentation_prompt(
            code, file_path, **kwargs
        )

        return self._generate_text(prompt)

    def generate_architecture_description(
        self, code: str, file_path: str, **kwargs
    ) -> str:
        """Generate architectural analysis for the given code."""
        logger.info(f"🏗️  Generating architecture description for {file_path}")

        # Build prompt using prompt manager
        prompt = self.prompt_manager.build_architecture_prompt(
            code, file_path, **kwargs
        )
        return self._generate_text(prompt)

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
            "quantization": (self.quantization if not self.is_mac else "8bit (MLX)"),
            "offline_mode": self.offline_mode,
            "check_for_updates": self.check_for_updates,
            "local_files_only": self.local_files_only,
        }


def create_model(config: Optional[Dict[str, Any]] = None) -> AIModel:
    """
    Create an AI model instance based on platform and configuration.

    Args:
        config: Optional configuration dictionary

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
