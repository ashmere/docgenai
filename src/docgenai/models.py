import logging
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoTokenizer, pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the MMaDA submodule to the Python path
mmada_path = Path(__file__).parent.parent.parent / "external" / "MMaDA"
if mmada_path.exists():
    sys.path.insert(0, str(mmada_path))
    try:
        from models import MMadaModelLM

        MMADA_AVAILABLE = True
        logger.info("✅ MMaDA native models available")
    except ImportError as e:
        logger.warning(f"❌ MMaDA native models not available: {e}")
        MMADA_AVAILABLE = False
else:
    logger.warning("❌ MMaDA submodule path not found")
    MMADA_AVAILABLE = False


class AIModel(ABC):
    """
    Abstract base class for AI models.
    This provides a common interface for different model implementations,
    making them swappable.
    """

    @abstractmethod
    def analyze_code(self, code: str) -> str:
        """Analyzes code and returns a textual description."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generates text from a prompt."""
        pass

    @abstractmethod
    def generate_image(self, prompt: str) -> Image.Image:
        """Generates an image from a prompt."""
        pass

    @abstractmethod
    def generate_with_reasoning(self, prompt: str) -> dict:
        """
        Generates content (text, image, etc.) along with the model's
        reasoning process.
        """
        pass

    def generate_documentation(self, prompt: str) -> str:
        """Generates documentation based on a prompt."""
        pass

    @abstractmethod
    def generate_diagram(self, code: str) -> str:
        """Generates a diagram from code."""
        pass


class MMaDANativeModel(AIModel):
    """
    Native MMaDA model implementation using the actual MMaDA codebase.
    """

    def __init__(
        self,
        model_name: str,
        hugging_face_token: str = None,
        quantization: str = "8bit",
        generation_cache=None,
    ):
        if not MMADA_AVAILABLE:
            raise ImportError(
                "MMaDA native models not available. "
                "Make sure the submodule is properly initialized."
            )

        logger.info(f"🔧 Initializing MMaDA model: {model_name}")
        logger.info(f"⚙️  Quantization: {quantization}")

        self.model_name = model_name
        self.hugging_face_token = hugging_face_token
        self.quantization = quantization
        self.generation_cache = generation_cache
        self._model = None
        self._tokenizer = None

    def _get_quantization_config(self):
        """Get torch dtype and quantization config based on setting"""
        logger.info("🔍 Checking quantization support...")

        # Check if bitsandbytes is available for quantization
        try:
            import bitsandbytes  # noqa: F401

            bnb_available = True
            logger.info("✅ bitsandbytes available for quantization")
        except ImportError:
            bnb_available = False
            logger.warning("❌ bitsandbytes not available")

        if self.quantization == "none":
            logger.info("📊 Using full precision (no quantization)")
            return torch.bfloat16, {}
        elif self.quantization == "8bit" and bnb_available:
            logger.info("📊 Using 8-bit quantization")
            return torch.bfloat16, {"load_in_8bit": True}
        elif self.quantization == "4bit" and bnb_available:
            logger.info("📊 Using 4-bit quantization")
            return torch.bfloat16, {"load_in_4bit": True}
        else:
            if not bnb_available and self.quantization != "none":
                logger.warning(
                    f"⚠️  {self.quantization} quantization requested but "
                    f"bitsandbytes not available. Using full precision."
                )
            return torch.bfloat16, {}

    def _initialize_model(self):
        if self._model is None:
            start_time = time.time()
            logger.info(f"🚀 Starting model initialization: {self.model_name}")

            try:
                # Step 1: Get quantization config
                logger.info("📋 Step 1/4: Configuring quantization...")
                dtype, quant_config = self._get_quantization_config()

                # Step 2: Load the main model
                logger.info("📥 Step 2/4: Loading MMaDA model...")
                logger.info("⏳ This may take several minutes on first run...")

                model_start = time.time()
                self._model = MMadaModelLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    torch_dtype=dtype,
                    token=self.hugging_face_token,
                    **quant_config,
                ).eval()
                model_time = time.time() - model_start

                logger.info(f"✅ Model loaded in {model_time:.2f} seconds")

                # Step 3: Load tokenizer
                logger.info("📥 Step 3/4: Loading tokenizer...")
                tokenizer_start = time.time()

                try:
                    self._tokenizer = AutoTokenizer.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        token=self.hugging_face_token,
                    )
                    tokenizer_time = time.time() - tokenizer_start
                    logger.info(f"✅ Tokenizer loaded in {tokenizer_time:.2f} seconds")
                except Exception as tokenizer_error:
                    logger.warning(f"❌ Tokenizer failed: {tokenizer_error}")
                    logger.info("🔄 Attempting fallback tokenizer...")

                    self._tokenizer = AutoTokenizer.from_pretrained(
                        "microsoft/DialoGPT-medium", trust_remote_code=True
                    )
                    if self._tokenizer.pad_token is None:
                        self._tokenizer.pad_token = self._tokenizer.eos_token
                    logger.info("✅ Using DialoGPT tokenizer as fallback")

                # Step 4: Setup chat template
                logger.info("📝 Step 4/4: Setting up chat template...")
                if hasattr(self._tokenizer, "chat_template"):
                    chat_template = (
                        "{% set loop_messages = messages %}"
                        "{% for message in loop_messages %}"
                        "{% set content = '<|start_header_id|>' + "
                        "message['role'] + '<|end_header_id|>\\n'+ "
                        "message['content'] | trim + '<|eot_id|>' %}"
                        "{% if loop.index0 == 0 %}"
                        "{% set content = bos_token + content %}"
                        "{% endif %}"
                        "{{ content }}"
                        "{% endfor %}"
                        "{{ '<|start_header_id|>assistant<|end_header_id|>\\n' }}"
                    )
                    self._tokenizer.chat_template = chat_template

                total_time = time.time() - start_time
                logger.info(
                    f"🎉 Model initialization complete! "
                    f"Total time: {total_time:.2f} seconds"
                )

            except Exception as e:
                logger.error(f"💥 Model initialization failed: {e}")
                logger.error("This may be due to:")
                logger.error("  - Insufficient memory")
                logger.error("  - Network connectivity issues")
                logger.error("  - Missing dependencies")
                logger.error("  - Platform compatibility (try Docker)")
                raise

    def _mmada_generate(self, prompt: str, max_length: int = 128) -> str:
        """Use MMaDA's native generation function."""
        logger.info("🎯 Starting text generation...")
        start_time = time.time()

        # Import the generate function from the MMaDA codebase
        sys.path.insert(0, str(mmada_path))
        from generate import generate

        # Prepare the prompt as a chat message
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = self._tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False
        )

        # Tokenize the input
        input_ids = self._tokenizer(
            text=formatted_prompt, return_tensors="pt", padding=True
        )["input_ids"]

        if torch.cuda.is_available():
            input_ids = input_ids.to("cuda")
            self._model = self._model.to("cuda")

        # Generate using MMaDA's native function
        logger.info("⚡ Running model inference...")
        output = generate(
            self._model,
            input_ids,
            steps=64,  # Reduced for faster generation
            gen_length=max_length,
            block_length=max_length,
            temperature=0.7,
            cfg_scale=0.0,
            remasking="low_confidence",
        )

        # Decode the output
        generated_text = self._tokenizer.batch_decode(
            output[:, input_ids.shape[1] :], skip_special_tokens=True
        )[0]

        generation_time = time.time() - start_time
        logger.info(f"✅ Generation completed in {generation_time:.2f} seconds")

        return generated_text.strip()

    def analyze_code(self, code: str) -> str:
        """Analyzes code using native MMaDA."""
        # Check cache first
        if self.generation_cache:
            cached_result = self.generation_cache.get(code, "analyze_code")
            if cached_result:
                print("Using cached analysis result")
                return cached_result

        self._initialize_model()
        prompt = (
            "Please analyze the following code and provide a detailed "
            "summary of its functionality, architecture, and potential "
            "improvements. Think step by step about the code structure "
            "and design patterns.\n\n"
            f"```\n{code}\n```\n\n"
            "Analysis:"
        )
        result = self._mmada_generate(prompt, max_length=256)

        # Cache the result
        if self.generation_cache:
            self.generation_cache.set(code, result, "analyze_code")

        return result

    def generate_text(self, prompt: str) -> str:
        """Generates text using native MMaDA."""
        # Check cache first
        if self.generation_cache:
            cached_result = self.generation_cache.get(prompt, "generate_text")
            if cached_result:
                print("Using cached generation result")
                return cached_result

        self._initialize_model()
        result = self._mmada_generate(prompt, max_length=128)

        # Cache the result
        if self.generation_cache:
            self.generation_cache.set(prompt, result, "generate_text")

        return result

    def generate_image(self, prompt: str) -> Image.Image:
        """MMaDA supports image generation, but not implemented yet."""
        print(f"Native MMaDA image generation for: '{prompt}'")
        return Image.new("RGB", (512, 512), color="lightgreen")

    def generate_with_reasoning(self, prompt: str) -> dict:
        """Generate with reasoning using MMaDA's CoT capabilities."""
        self._initialize_model()

        reasoning_prompt = (
            "Think step by step about this request and provide detailed "
            "reasoning:\n"
            f"{prompt}\n\n"
            "Let me think through this systematically:"
        )

        explanation_prompt = (
            f"Based on the following request, provide a comprehensive "
            f"explanation:\n"
            f"{prompt}\n\n"
            "Explanation:"
        )

        reasoning = self._mmada_generate(reasoning_prompt, max_length=256)
        explanation = self._mmada_generate(explanation_prompt, max_length=256)

        return {
            "reasoning": reasoning,
            "explanation": explanation,
            "diagram": self.generate_image(f"Diagram for: {prompt}"),
            "suggestions": self._mmada_generate(
                f"Provide improvement suggestions for: {prompt}", max_length=128
            ),
        }

    def generate_documentation(self, prompt: str) -> str:
        """Generate documentation using native MMaDA."""
        self._initialize_model()
        doc_prompt = (
            "Generate comprehensive technical documentation for the "
            "following. Include purpose, functionality, usage examples, "
            "and best practices:\n\n"
            f"{prompt}\n\n"
            "Documentation:"
        )
        return self._mmada_generate(doc_prompt, max_length=512)

    def generate_diagram(self, code: str) -> str:
        """Generate Mermaid diagram using native MMaDA."""
        self._initialize_model()
        diagram_prompt = (
            "Analyze the following code and create a Mermaid.js diagram "
            "that represents its structure, flow, or architecture. "
            "Respond only with the Mermaid syntax:\n\n"
            f"```\n{code}\n```\n\n"
            "Mermaid diagram:"
        )
        return self._mmada_generate(diagram_prompt, max_length=256)


class MMaDAModel(AIModel):
    """
    Fallback MMaDA model implementation using transformers pipeline.
    Used when the native MMaDA implementation is not available.
    """

    def __init__(self, model_name: str, hugging_face_token: str = None):
        self.model_name = model_name
        self.hugging_face_token = hugging_face_token
        self._pipeline = None

    def _initialize_pipeline(self):
        if self._pipeline is None:
            print(f"Initializing fallback model for: {self.model_name}")
            try:
                # Fallback to a working model
                self._pipeline = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    trust_remote_code=True,
                    token=self.hugging_face_token,
                )
                print("Fallback to DialoGPT-medium successful.")
            except Exception as e:
                print(f"Fallback initialization failed: {e}")
                self._pipeline = None

    def analyze_code(self, code: str) -> str:
        """Analyzes code using fallback model."""
        prompt = (
            "Please analyze the following code and provide a detailed "
            "summary of its functionality:\n\n"
            f"```\n{code}\n```\n\n"
            "Analysis:"
        )
        return self.generate_text(prompt)

    def generate_text(self, prompt: str) -> str:
        """Generates text using fallback model."""
        self._initialize_pipeline()

        if self._pipeline:
            try:
                result = self._pipeline(
                    prompt,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self._pipeline.tokenizer.eos_token_id,
                )
                generated_text = result[0]["generated_text"]
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt) :].strip()
                return generated_text
            except Exception as e:
                return f"Error: Could not generate text - {str(e)}"

        return "No model available for text generation."

    def generate_image(self, prompt: str) -> Image.Image:
        """Fallback image generation."""
        print(f"Fallback image generation for: '{prompt}'")
        return Image.new("RGB", (512, 512), color="lightblue")

    def generate_with_reasoning(self, prompt: str) -> dict:
        """Generate with reasoning using fallback model."""
        reasoning = self.generate_text(f"Think step by step about: {prompt}")
        explanation = self.generate_text(
            f"Provide a comprehensive explanation for: {prompt}"
        )

        return {
            "reasoning": reasoning,
            "explanation": explanation,
            "diagram": self.generate_image(f"Diagram for: {prompt}"),
            "suggestions": self.generate_text(
                f"Provide improvement suggestions for: {prompt}"
            ),
        }

    def generate_documentation(self, prompt: str) -> str:
        """Generate documentation using fallback model."""
        doc_prompt = (
            "Generate comprehensive technical documentation for the "
            "following:\n\n"
            f"{prompt}\n\n"
            "Documentation:"
        )
        return self.generate_text(doc_prompt)

    def generate_diagram(self, code: str) -> str:
        """Generate Mermaid diagram using fallback model."""
        diagram_prompt = (
            "Create a Mermaid.js diagram for the following code. "
            "Respond only with the Mermaid syntax:\n\n"
            f"```\n{code}\n```\n\n"
            "Mermaid diagram:"
        )
        return self.generate_text(diagram_prompt)
