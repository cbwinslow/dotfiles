"""
Letta Model Picker - GPU-enabled llama.cpp and embedding model selection

This module provides:
- GPU llama.cpp model support
- Embedding model endpoint selection
- Model configuration management
- Hardware acceleration detection

Usage:
    from letta_model_picker import ModelPicker, LLMConfig, EmbeddingConfig
    
    # Pick GPU-enabled model
    picker = ModelPicker()
    picker.configure_gpu_llama(model_path="/path/to/model.gguf", n_gpu_layers=35)
    
    # Or use Ollama endpoint
    picker.use_ollama(model_name="llama3.1:8b", embedding_model="nomic-embed-text")
    
    # Get config for agent creation
    config = picker.get_config()
    letta.create_agent("myagent", model_config=config)

Location: ~/dotfiles/ai/packages/letta_integration/letta_model_picker.py
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported model providers"""
    LLAMA_CPP = "llama.cpp"          # GPU-enabled local llama.cpp
    OLLAMA = "ollama"                 # Ollama server
    OPENROUTER = "openrouter"         # OpenRouter API
    LETTA_FREE = "letta-free"         # Letta's free model
    CUSTOM = "custom"                 # Custom endpoint


class EmbeddingProvider(Enum):
    """Supported embedding providers"""
    OLLAMA = "ollama"                 # Ollama embeddings
    LLAMA_CPP = "llama.cpp"          # llama.cpp embeddings  
    OPENAI = "openai"                 # OpenAI embeddings
    HUGGINGFACE = "huggingface"       # HuggingFace embeddings
    BGE_M3 = "bge-m3"                 # BGE-M3 via Ollama
    NOMIC = "nomic-embed-text"        # Nomic via Ollama


@dataclass
class GPUConfig:
    """
    GPU configuration for llama.cpp models.
    
    Attributes:
        enabled: Whether to use GPU acceleration
        n_gpu_layers: Number of layers to offload to GPU (0 = CPU only)
        main_gpu: Primary GPU device ID
        tensor_split: GPU memory split ratios for multi-GPU
        use_mlock: Lock model in memory
        use_mmap: Use memory mapping
    """
    enabled: bool = True
    n_gpu_layers: int = 35  # Offload most layers to GPU
    main_gpu: int = 0
    tensor_split: List[float] = field(default_factory=list)
    use_mlock: bool = False
    use_mmap: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LLMConfig:
    """
    LLM model configuration.
    
    This class defines how the language model is loaded and used.
    Supports GPU llama.cpp, Ollama, and remote APIs.
    
    Attributes:
        provider: Model provider type
        model_name: Name or path of the model
        model_path: Local path to .gguf file (for llama.cpp)
        context_length: Max context window size
        temperature: Sampling temperature (0.0-2.0)
        top_p: Nucleus sampling parameter
        max_tokens: Maximum tokens to generate
        stop_sequences: Sequences that stop generation
        gpu_config: GPU configuration for llama.cpp
        api_url: Custom API endpoint URL
        api_key: API key for remote services
        
    Example:
        # GPU llama.cpp configuration
        config = LLMConfig(
            provider=ModelProvider.LLAMA_CPP,
            model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
            context_length=8192,
            gpu_config=GPUConfig(n_gpu_layers=35)
        )
        
        # Ollama configuration
        config = LLMConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama3.1:8b",
            context_length=128000
        )
    """
    provider: ModelProvider = ModelProvider.LETTA_FREE
    model_name: str = "letta-free"
    model_path: Optional[str] = None
    context_length: int = 8192
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stop_sequences: List[str] = field(default_factory=list)
    gpu_config: Optional[GPUConfig] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['provider'] = self.provider.value
        if self.gpu_config:
            data['gpu_config'] = self.gpu_config.to_dict()
        return data
    
    def to_letta_format(self) -> str:
        """Convert to Letta API format"""
        if self.provider == ModelProvider.LLAMA_CPP and self.model_path:
            return f"llama.cpp/{self.model_path}"
        elif self.provider == ModelProvider.OLLAMA:
            return f"ollama/{self.model_name}"
        elif self.provider == ModelProvider.OPENROUTER:
            return f"openrouter/{self.model_name}"
        elif self.provider == ModelProvider.LETTA_FREE:
            return "letta/letta-free"
        else:
            return self.model_name


@dataclass
class EmbeddingConfig:
    """
    Embedding model configuration.
    
    Defines how text embeddings are generated for memory storage
    and retrieval.
    
    Attributes:
        provider: Embedding provider type
        model_name: Name of the embedding model
        model_path: Local path to embedding model
        dimensions: Embedding vector dimensions
        normalize: Whether to normalize embeddings
        batch_size: Batch processing size
        api_url: Custom embedding endpoint
        api_key: API key for remote services
        
    Example:
        # Ollama BGE-M3 (high quality, good for RAG)
        config = EmbeddingConfig(
            provider=EmbeddingProvider.BGE_M3,
            model_name="bge-m3:latest",
            dimensions=1024
        )
        
        # Nomic (fast, good quality)
        config = EmbeddingConfig(
            provider=EmbeddingProvider.NOMIC,
            model_name="nomic-embed-text:latest",
            dimensions=768
        )
    """
    provider: EmbeddingProvider = EmbeddingProvider.BGE_M3
    model_name: str = "bge-m3:latest"
    model_path: Optional[str] = None
    dimensions: int = 1024
    normalize: bool = True
    batch_size: int = 32
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['provider'] = self.provider.value
        return data
    
    def to_letta_format(self) -> str:
        """Convert to Letta API format"""
        if self.provider == EmbeddingProvider.OLLAMA:
            return f"ollama/{self.model_name}"
        elif self.provider == EmbeddingProvider.LLAMA_CPP and self.model_path:
            return f"llama.cpp/{self.model_path}"
        elif self.provider == EmbeddingProvider.BGE_M3:
            return f"ollama/bge-m3:latest"
        elif self.provider == EmbeddingProvider.NOMIC:
            return f"ollama/nomic-embed-text:latest"
        else:
            return self.model_name


class ModelPicker:
    """
    Model picker for GPU-enabled llama.cpp and embedding models.
    
    This class helps configure and select models for Letta agents.
    It provides:
    - GPU detection and configuration
    - Model preset management
    - Hardware-optimized settings
    - Easy switching between providers
    
    Usage:
        picker = ModelPicker()
        
        # Use GPU llama.cpp
        picker.configure_gpu_llama(
            model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
            n_gpu_layers=35
        )
        
        # Or use Ollama
        picker.use_ollama(
            llm_model="llama3.1:8b",
            embedding_model="nomic-embed-text:latest"
        )
        
        # Get configuration
        llm_config, embedding_config = picker.get_config()
    
    Presets Available:
    - fast_gpu: Optimized for speed on GPU
    - quality_gpu: Optimized for quality on GPU
    - cpu_fallback: CPU-only configuration
    - ollama_standard: Standard Ollama setup
    """
    
    # Predefined model presets
    PRESETS = {
        "fast_gpu": {
            "description": "Fast inference with GPU acceleration",
            "llm": {
                "provider": ModelProvider.LLAMA_CPP,
                "model_path": None,  # Must be specified
                "context_length": 4096,
                "temperature": 0.7,
                "gpu_config": GPUConfig(n_gpu_layers=35, enabled=True)
            },
            "embedding": {
                "provider": EmbeddingProvider.NOMIC,
                "model_name": "nomic-embed-text:latest",
                "dimensions": 768
            }
        },
        "quality_gpu": {
            "description": "High quality with full GPU utilization",
            "llm": {
                "provider": ModelProvider.LLAMA_CPP,
                "model_path": None,
                "context_length": 8192,
                "temperature": 0.6,
                "gpu_config": GPUConfig(n_gpu_layers=99, enabled=True)
            },
            "embedding": {
                "provider": EmbeddingProvider.BGE_M3,
                "model_name": "bge-m3:latest",
                "dimensions": 1024
            }
        },
        "cpu_fallback": {
            "description": "CPU-only fallback (no GPU)",
            "llm": {
                "provider": ModelProvider.OLLAMA,
                "model_name": "llama3.1:8b",
                "context_length": 4096,
                "temperature": 0.7
            },
            "embedding": {
                "provider": EmbeddingProvider.NOMIC,
                "model_name": "nomic-embed-text:latest",
                "dimensions": 768
            }
        },
        "ollama_standard": {
            "description": "Standard Ollama setup",
            "llm": {
                "provider": ModelProvider.OLLAMA,
                "model_name": "llama3.1:8b",
                "context_length": 128000,
                "temperature": 0.7
            },
            "embedding": {
                "provider": EmbeddingProvider.BGE_M3,
                "model_name": "bge-m3:latest",
                "dimensions": 1024
            }
        },
        "letta_free": {
            "description": "Letta's built-in free model",
            "llm": {
                "provider": ModelProvider.LETTA_FREE,
                "model_name": "letta-free",
                "context_length": 4096
            },
            "embedding": {
                "provider": EmbeddingProvider.BGE_M3,
                "model_name": "bge-m3:latest",
                "dimensions": 1024
            }
        }
    }
    
    def __init__(self):
        """Initialize model picker with default configuration"""
        self.llm_config = LLMConfig()
        self.embedding_config = EmbeddingConfig()
        self.gpu_available = self._check_gpu_availability()
        logger.info(f"ModelPicker initialized. GPU available: {self.gpu_available}")
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for acceleration"""
        try:
            # Check for NVIDIA GPU
            result = subprocess.run(
                ["nvidia-smi"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("NVIDIA GPU detected")
                return True
        except:
            pass
        
        try:
            # Check for AMD GPU
            result = subprocess.run(
                ["rocm-smi"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("AMD GPU detected")
                return True
        except:
            pass
        
        logger.info("No GPU detected, using CPU")
        return False
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get detailed GPU information"""
        info = {
            "available": self.gpu_available,
            "devices": [],
            "driver_version": None,
            "cuda_version": None
        }
        
        if not self.gpu_available:
            return info
        
        try:
            # NVIDIA GPU info
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "," in line:
                        name, memory = line.split(",")
                        info["devices"].append({
                            "name": name.strip(),
                            "memory": memory.strip()
                        })
            
            # Driver version
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "Driver Version:" in line:
                        info["driver_version"] = line.split("Driver Version:")[1].split()[0]
                    if "CUDA Version:" in line:
                        info["cuda_version"] = line.split("CUDA Version:")[1].split()[0]
        except:
            pass
        
        return info
    
    def configure_gpu_llama(
        self,
        model_path: str,
        n_gpu_layers: int = 35,
        context_length: int = 8192,
        temperature: float = 0.7,
        main_gpu: int = 0
    ) -> None:
        """
        Configure GPU-enabled llama.cpp model.
        
        Args:
            model_path: Path to .gguf model file
            n_gpu_layers: Number of layers to offload to GPU (0-99)
            context_length: Context window size
            temperature: Sampling temperature
            main_gpu: Primary GPU device ID
            
        Example:
            picker.configure_gpu_llama(
                model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
                n_gpu_layers=35
            )
        """
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
        
        gpu_config = GPUConfig(
            enabled=self.gpu_available,
            n_gpu_layers=n_gpu_layers if self.gpu_available else 0,
            main_gpu=main_gpu
        )
        
        self.llm_config = LLMConfig(
            provider=ModelProvider.LLAMA_CPP,
            model_name=os.path.basename(model_path),
            model_path=model_path,
            context_length=context_length,
            temperature=temperature,
            gpu_config=gpu_config
        )
        
        logger.info(f"Configured GPU llama.cpp: {model_path} ({n_gpu_layers} layers on GPU)")
    
    def use_ollama(
        self,
        llm_model: str = "llama3.1:8b",
        embedding_model: str = "bge-m3:latest",
        context_length: int = 128000,
        api_url: str = "http://localhost:11434"
    ) -> None:
        """
        Configure Ollama as the model provider.
        
        Args:
            llm_model: Ollama model name for LLM
            embedding_model: Ollama model name for embeddings
            context_length: Context window size
            api_url: Ollama API URL
            
        Example:
            picker.use_ollama(
                llm_model="llama3.1:8b",
                embedding_model="nomic-embed-text:latest"
            )
        """
        self.llm_config = LLMConfig(
            provider=ModelProvider.OLLAMA,
            model_name=llm_model,
            context_length=context_length,
            api_url=api_url
        )
        
        # Determine embedding provider from model name
        if "nomic" in embedding_model.lower():
            embedding_provider = EmbeddingProvider.NOMIC
            dimensions = 768
        elif "bge" in embedding_model.lower():
            embedding_provider = EmbeddingProvider.BGE_M3
            dimensions = 1024
        else:
            embedding_provider = EmbeddingProvider.OLLAMA
            dimensions = 1024
        
        self.embedding_config = EmbeddingConfig(
            provider=embedding_provider,
            model_name=embedding_model,
            dimensions=dimensions,
            api_url=api_url
        )
        
        logger.info(f"Configured Ollama: LLM={llm_model}, Embedding={embedding_model}")
    
    def use_openrouter(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        context_length: int = 128000
    ) -> None:
        """
        Configure OpenRouter as the model provider.
        
        Args:
            model_name: OpenRouter model identifier
            api_key: OpenRouter API key
            context_length: Context window size
        """
        self.llm_config = LLMConfig(
            provider=ModelProvider.OPENROUTER,
            model_name=model_name,
            context_length=context_length,
            api_key=api_key or os.getenv("OPENROUTER_API_KEY")
        )
        
        # Keep default embedding (BGE-M3 via Ollama)
        logger.info(f"Configured OpenRouter: {model_name}")
    
    def apply_preset(self, preset_name: str, **overrides) -> None:
        """
        Apply a predefined model configuration preset.
        
        Args:
            preset_name: Name of the preset to apply
            **overrides: Override any preset values
            
        Available Presets:
            - fast_gpu: Fast inference with GPU
            - quality_gpu: High quality with full GPU
            - cpu_fallback: CPU-only
            - ollama_standard: Standard Ollama
            - letta_free: Letta's free model
            
        Example:
            picker.apply_preset("fast_gpu", model_path="/path/to/model.gguf")
        """
        if preset_name not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.PRESETS.keys())}")
        
        preset = self.PRESETS[preset_name]
        
        # Apply LLM config
        llm_data = preset["llm"].copy()
        llm_data.update(overrides)
        
        if "gpu_config" in llm_data and llm_data["gpu_config"]:
            llm_data["gpu_config"] = GPUConfig(**llm_data["gpu_config"])
        
        self.llm_config = LLMConfig(**llm_data)
        
        # Apply embedding config
        self.embedding_config = EmbeddingConfig(**preset["embedding"])
        
        logger.info(f"Applied preset: {preset_name} - {preset['description']}")
    
    def list_presets(self) -> List[Dict[str, str]]:
        """List all available presets with descriptions"""
        return [
            {"name": name, "description": preset["description"]}
            for name, preset in self.PRESETS.items()
        ]
    
    def get_config(self) -> tuple[LLMConfig, EmbeddingConfig]:
        """
        Get current LLM and embedding configuration.
        
        Returns:
            Tuple of (LLMConfig, EmbeddingConfig)
        """
        return self.llm_config, self.embedding_config
    
    def to_letta_agent_config(self) -> Dict[str, Any]:
        """
        Convert configuration to Letta agent creation format.
        
        Returns:
            Dictionary for Letta API agent creation
        """
        return {
            "model": self.llm_config.to_letta_format(),
            "embedding": self.embedding_config.to_letta_format()
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get detailed information about current model configuration.
        
        Returns:
            Dictionary with model details for agent awareness
        """
        gpu_info = self.get_gpu_info()
        
        return {
            "llm": {
                "provider": self.llm_config.provider.value,
                "model_name": self.llm_config.model_name,
                "model_path": self.llm_config.model_path,
                "context_length": self.llm_config.context_length,
                "temperature": self.llm_config.temperature,
                "using_gpu": self.llm_config.gpu_config.enabled if self.llm_config.gpu_config else False,
                "gpu_layers": self.llm_config.gpu_config.n_gpu_layers if self.llm_config.gpu_config else 0,
            },
            "embedding": {
                "provider": self.embedding_config.provider.value,
                "model_name": self.embedding_config.model_name,
                "dimensions": self.embedding_config.dimensions,
                "normalize": self.embedding_config.normalize,
            },
            "hardware": {
                "gpu_available": self.gpu_available,
                "gpu_info": gpu_info,
            },
            "recommended_for": self._get_recommended_use_cases()
        }
    
    def _get_recommended_use_cases(self) -> List[str]:
        """Get recommended use cases based on configuration"""
        use_cases = []
        
        if self.llm_config.provider == ModelProvider.LLAMA_CPP:
            if self.llm_config.gpu_config and self.llm_config.gpu_config.enabled:
                use_cases.append("Fast local inference with GPU acceleration")
                use_cases.append("Privacy-preserving (no data leaves local machine)")
                if self.llm_config.gpu_config.n_gpu_layers > 30:
                    use_cases.append("High-performance reasoning tasks")
            else:
                use_cases.append("CPU-only inference (slower)")
                use_cases.append("Low-resource environments")
        
        elif self.llm_config.provider == ModelProvider.OLLAMA:
            use_cases.append("Easy model management")
            use_cases.append("Multiple model support")
            use_cases.append("GPU acceleration via Ollama")
        
        elif self.llm_config.provider == ModelProvider.OPENROUTER:
            use_cases.append("Access to many models")
            use_cases.append("No local GPU required")
            use_cases.append("API-based (requires internet)")
        
        # Embedding recommendations
        if self.embedding_config.provider == EmbeddingProvider.BGE_M3:
            use_cases.append("High-quality semantic search (BGE-M3)")
        elif self.embedding_config.provider == EmbeddingProvider.NOMIC:
            use_cases.append("Fast embedding generation (Nomic)")
        
        return use_cases
    
    def print_config(self) -> None:
        """Print current configuration in a readable format"""
        info = self.get_model_info()
        
        print("\n" + "="*60)
        print("MODEL CONFIGURATION")
        print("="*60)
        
        print("\n📊 LLM Model:")
        print(f"  Provider: {info['llm']['provider']}")
        print(f"  Model: {info['llm']['model_name']}")
        if info['llm']['model_path']:
            print(f"  Path: {info['llm']['model_path']}")
        print(f"  Context: {info['llm']['context_length']} tokens")
        print(f"  Temperature: {info['llm']['temperature']}")
        print(f"  GPU Enabled: {info['llm']['using_gpu']}")
        if info['llm']['using_gpu']:
            print(f"  GPU Layers: {info['llm']['gpu_layers']}")
        
        print("\n🔤 Embedding Model:")
        print(f"  Provider: {info['embedding']['provider']}")
        print(f"  Model: {info['embedding']['model_name']}")
        print(f"  Dimensions: {info['embedding']['dimensions']}")
        print(f"  Normalize: {info['embedding']['normalize']}")
        
        print("\n💻 Hardware:")
        print(f"  GPU Available: {info['hardware']['gpu_available']}")
        if info['hardware']['gpu_info']['devices']:
            for i, device in enumerate(info['hardware']['gpu_info']['devices']):
                print(f"  GPU {i}: {device['name']} ({device['memory']})")
        
        print("\n✅ Recommended For:")
        for use_case in info['recommended_for']:
            print(f"  • {use_case}")
        
        print("="*60 + "\n")


# Convenience functions
def create_gpu_config(
    model_path: str,
    n_gpu_layers: int = 35,
    embedding_model: str = "nomic-embed-text:latest"
) -> tuple[LLMConfig, EmbeddingConfig]:
    """
    Quick function to create GPU-enabled configuration.
    
    Args:
        model_path: Path to .gguf model file
        n_gpu_layers: GPU layers to use
        embedding_model: Embedding model name
        
    Returns:
        Tuple of (LLMConfig, EmbeddingConfig)
    """
    picker = ModelPicker()
    picker.configure_gpu_llama(model_path, n_gpu_layers)
    
    # Set embedding model
    if "nomic" in embedding_model:
        picker.embedding_config = EmbeddingConfig(
            provider=EmbeddingProvider.NOMIC,
            model_name=embedding_model,
            dimensions=768
        )
    else:
        picker.embedding_config = EmbeddingConfig(
            provider=EmbeddingProvider.BGE_M3,
            model_name=embedding_model,
            dimensions=1024
        )
    
    return picker.get_config()


def create_ollama_config(
    llm_model: str = "llama3.1:8b",
    embedding_model: str = "bge-m3:latest"
) -> tuple[LLMConfig, EmbeddingConfig]:
    """
    Quick function to create Ollama configuration.
    
    Args:
        llm_model: Ollama LLM model name
        embedding_model: Ollama embedding model name
        
    Returns:
        Tuple of (LLMConfig, EmbeddingConfig)
    """
    picker = ModelPicker()
    picker.use_ollama(llm_model, embedding_model)
    return picker.get_config()


def get_current_models() -> Dict[str, Any]:
    """
    Get information about currently configured models.
    Use this to inform agents what models they are using.
    """
    picker = ModelPicker()
    return picker.get_model_info()


if __name__ == "__main__":
    # Demo usage
    picker = ModelPicker()
    
    # Show available presets
    print("\nAvailable Presets:")
    for preset in picker.list_presets():
        print(f"  {preset['name']}: {preset['description']}")
    
    # Print current config
    picker.print_config()
    
    # Example: Apply fast GPU preset
    # picker.apply_preset("fast_gpu", model_path="/path/to/model.gguf")
