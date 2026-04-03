# Letta Model Picker Skill

**Purpose:** GPU-enabled model selection and configuration for Letta agents  
**Location:** `~/dotfiles/ai/packages/letta_integration/letta_model_picker.py`  
**Integration:** `~/dotfiles/ai/packages/letta_integration/letta_integration/__init__.py`

---

## Overview

This skill provides comprehensive model selection and configuration for Letta agents, supporting:

- **GPU-enabled llama.cpp models** - Local GPU acceleration for fast inference
- **Ollama integration** - Easy model management with GPU support
- **Embedding model selection** - Choose between BGE-M3, Nomic, or custom embeddings
- **Model presets** - Quick configuration for common use cases
- **Hardware detection** - Automatic GPU detection and optimization

---

## Features

### Supported Model Providers

| Provider | Type | GPU Support | Use Case |
|----------|------|-------------|----------|
| llama.cpp | Local | ✅ NVIDIA/AMD | Fast local inference |
| Ollama | Local/Remote | ✅ GPU | Easy model management |
| OpenRouter | API | ❌ | Many models, no GPU needed |
| Letta Free | Built-in | ❌ | Default fallback |

### Supported Embedding Providers

| Provider | Model | Dimensions | Speed | Quality |
|----------|-------|------------|-------|---------|
| BGE-M3 | bge-m3:latest | 1024 | Medium | Excellent |
| Nomic | nomic-embed-text:latest | 768 | Fast | Good |
| Ollama | Various | Varies | Medium | Varies |

---

## Quick Start

### Basic Usage

```python
from letta_integration import LettaIntegration

# Initialize with default Ollama models
letta = LettaIntegration(agent_name="windsurf")

# Configure GPU llama.cpp
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

# Create agent with configured models
agent = letta.create_agent_with_config("myagent")
```

### Using Model Presets

```python
# Apply preset configuration
letta.apply_model_preset("fast_gpu")

# Available presets:
# - fast_gpu: Fast inference with GPU
# - quality_gpu: High quality with full GPU
# - cpu_fallback: CPU-only
# - ollama_standard: Standard Ollama
# - letta_free: Built-in free model
```

### Checking Current Models

```python
# Get model information
info = letta.get_current_model_info()
print(f"Using LLM: {info['llm']['model_name']}")
print(f"GPU Enabled: {info['llm']['using_gpu']}")

# Print formatted configuration
letta.print_model_info()
```

---

## Model Picker API

### Direct Model Picker Usage

```python
from letta_model_picker import ModelPicker, create_gpu_config, create_ollama_config

# Method 1: Using ModelPicker class
picker = ModelPicker()
picker.configure_gpu_llama(
    model_path="/path/to/model.gguf",
    n_gpu_layers=35
)
llm_config, embedding_config = picker.get_config()

# Method 2: Quick GPU config
llm_config, embedding_config = create_gpu_config(
    model_path="/path/to/model.gguf",
    n_gpu_layers=35,
    embedding_model="nomic-embed-text:latest"
)

# Method 3: Quick Ollama config
llm_config, embedding_config = create_ollama_config(
    llm_model="llama3.1:8b",
    embedding_model="bge-m3:latest"
)
```

### Configuration Classes

```python
from letta_model_picker import LLMConfig, EmbeddingConfig, GPUConfig, ModelProvider

# Create custom LLM config
llm_config = LLMConfig(
    provider=ModelProvider.LLAMA_CPP,
    model_path="/models/model.gguf",
    context_length=8192,
    temperature=0.7,
    gpu_config=GPUConfig(
        enabled=True,
        n_gpu_layers=35,
        main_gpu=0
    )
)

# Create custom embedding config
embedding_config = EmbeddingConfig(
    provider=EmbeddingProvider.BGE_M3,
    model_name="bge-m3:latest",
    dimensions=1024,
    normalize=True
)
```

---

## GPU Configuration

### NVIDIA GPU

```python
# Auto-detect GPU and configure
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35  # Offload 35 layers to GPU
)
```

### Multi-GPU Setup

```python
from letta_model_picker import GPUConfig

# Configure for multi-GPU
gpu_config = GPUConfig(
    enabled=True,
    n_gpu_layers=99,  # All layers on GPU
    main_gpu=0,
    tensor_split=[0.7, 0.3]  # 70% GPU 0, 30% GPU 1
)
```

### Checking GPU Availability

```python
# Check GPU info
picker = ModelPicker()
info = picker.get_gpu_info()
print(f"GPU Available: {info['available']}")
print(f"Devices: {info['devices']}")
```

---

## Integration with Letta

### Creating Agents with Custom Models

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

# Configure models
config = letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35,
    embedding_model="nomic-embed-text:latest"
)

# Create agent with config
result = letta.create_agent_with_config("windsurf", config)
print(f"Agent ID: {result['id']}")
```

### Using Ollama

```python
# Configure Ollama models
letta.configure_models(
    llm_model="llama3.1:8b",
    embedding_model="bge-m3:latest",
    use_ollama=True
)

# Or use preset
letta.apply_model_preset("ollama_standard")
```

---

## Model Presets

### Available Presets

| Preset | Description | LLM | Embedding | GPU |
|--------|-------------|-----|-----------|-----|
| `fast_gpu` | Fast inference | llama.cpp | nomic-embed-text | 35 layers |
| `quality_gpu` | High quality | llama.cpp | bge-m3 | 99 layers |
| `cpu_fallback` | CPU only | Ollama | nomic-embed-text | None |
| `ollama_standard` | Standard | Ollama | bge-m3 | Auto |
| `letta_free` | Free tier | letta-free | bge-m3 | None |

### Applying Presets

```python
# Apply with custom model path
letta.apply_model_preset("fast_gpu")
# Then set model path
letta.model_picker.llm_config.model_path = "/path/to/model.gguf"

# Create agent
config = letta.model_picker.to_letta_agent_config()
agent = letta.create_agent_with_config("myagent", config)
```

---

## Environment Variables

```bash
# Letta server
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-api-key"

# Ollama (if using Ollama provider)
export OLLAMA_HOST="http://localhost:11434"

# OpenRouter (if using OpenRouter provider)
export OPENROUTER_API_KEY="your-key"
```

---

## Command Line Usage

### Check GPU and Models

```bash
cd ~/dotfiles/ai/packages/letta_integration
python3 letta_model_picker.py
```

Output:
```
Available Presets:
  fast_gpu: Fast inference with GPU acceleration
  quality_gpu: High quality with full GPU utilization
  cpu_fallback: CPU-only fallback (no GPU)
  ollama_standard: Standard Ollama setup
  letta_free: Letta's built-in free model

============================================================
MODEL CONFIGURATION
============================================================

📊 LLM Model:
  Provider: ollama
  Model: llama3.1:8b
  Context: 128000 tokens
  GPU Enabled: True

🔤 Embedding Model:
  Provider: bge-m3
  Model: bge-m3:latest
  Dimensions: 1024

💻 Hardware:
  GPU Available: True
  GPU 0: NVIDIA RTX 4090 (24576 MiB)

✅ Recommended For:
  • Easy model management
  • Multiple model support
  • GPU acceleration via Ollama
  • High-quality semantic search (BGE-M3)

============================================================
```

---

## Best Practices

### GPU Layer Selection

```python
# For 8GB VRAM: 20-25 layers
# For 12GB VRAM: 30-35 layers
# For 16GB VRAM: 40-45 layers
# For 24GB VRAM: 50-60 layers
# For 48GB VRAM: 99 layers (all)

letta.configure_models(
    model_path="/models/model.gguf",
    n_gpu_layers=35  # Adjust based on VRAM
)
```

### Model Selection Guide

**For Speed:**
- Use `nomic-embed-text:latest` for embeddings (faster)
- Use llama.cpp with appropriate GPU layers
- Apply `fast_gpu` preset

**For Quality:**
- Use `bge-m3:latest` for embeddings (better quality)
- Use larger models (70B+ parameters)
- Apply `quality_gpu` preset with all layers on GPU

**For Privacy:**
- Use local llama.cpp models
- Use local Ollama instance
- Avoid OpenRouter for sensitive data

---

## Troubleshooting

### GPU Not Detected

```python
# Check GPU manually
picker = ModelPicker()
print(picker.get_gpu_info())

# Force CPU mode
picker.llm_config.gpu_config.enabled = False
```

### Model Loading Errors

```python
# Verify model path exists
import os
model_path = "/path/to/model.gguf"
if not os.path.exists(model_path):
    print(f"Model not found: {model_path}")

# Use Ollama as fallback
letta.configure_models(use_ollama=True)
```

### Memory Issues

```python
# Reduce GPU layers to free VRAM
letta.configure_models(
    model_path="/models/model.gguf",
    n_gpu_layers=20  # Reduce from 35
)

# Or use CPU fallback
letta.apply_model_preset("cpu_fallback")
```

---

## Integration with Agent Skills

### In Agent Configuration

```yaml
# In base_agent.yaml or agent config
skills:
  - model_picker  # Add to skills list

model_config:
  preset: "fast_gpu"  # or "ollama_standard"
  # Or custom:
  llm:
    provider: llama.cpp
    model_path: "/models/llama-3-8b-instruct.Q4_K_M.gguf"
    n_gpu_layers: 35
  embedding:
    provider: bge-m3
    model: "bge-m3:latest"
```

### In Agent Code

```python
# Agent knows what models it's using
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

# Get model info for agent awareness
info = letta.get_current_model_info()
print(f"""
Agent Configuration:
- LLM: {info['llm']['model_name']} ({info['llm']['provider']})
- GPU: {'Enabled' if info['llm']['using_gpu'] else 'Disabled'}
- Embedding: {info['embedding']['model_name']} ({info['embedding']['dimensions']}d)
""")
```

---

## API Reference

### ModelPicker Class

```python
class ModelPicker:
    def __init__(self)
    def configure_gpu_llama(model_path, n_gpu_layers=35, ...)
    def use_ollama(llm_model, embedding_model, ...)
    def use_openrouter(model_name, api_key, ...)
    def apply_preset(preset_name)
    def list_presets() -> List[Dict]
    def get_config() -> Tuple[LLMConfig, EmbeddingConfig]
    def to_letta_agent_config() -> Dict
    def get_model_info() -> Dict
    def print_config()
```

### LettaIntegration Methods

```python
class LettaIntegration:
    def configure_models(model_path, n_gpu_layers, ...)
    def create_agent_with_config(agent_name, model_config)
    def get_current_model_info()
    def print_model_info()
    def apply_model_preset(preset_name)
```

---

## Examples

### Complete Agent Setup with GPU

```python
from letta_integration import LettaIntegration

# Initialize
letta = LettaIntegration(agent_name="windsurf")

# Check current models
letta.print_model_info()

# Configure GPU llama.cpp
config = letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35,
    embedding_model="nomic-embed-text:latest"
)

# Create agent with GPU config
agent = letta.create_agent_with_config("windsurf", config)

# Setup core memory
letta.setup_core_memory_blocks(
    persona_value="I am Windsurf, a code editor AI...",
    human_value="User is a software developer..."
)

# Use agent
letta.save_conversation([
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! I'm ready to help."}
])
```

### Dynamic Model Switching

```python
# Start with CPU fallback
letta.apply_model_preset("cpu_fallback")

# Check if GPU available
if letta.model_picker.gpu_available:
    # Upgrade to GPU
    letta.apply_model_preset("fast_gpu")
    letta.model_picker.llm_config.model_path = "/models/model.gguf"
    
    # Recreate agent with GPU
    config = letta.model_picker.to_letta_agent_config()
    letta.create_agent_with_config("windsurf", config)
```

---

## Dependencies

- `requests` - HTTP client for API calls
- `letta_integration` - Core Letta integration
- `nvidia-smi` (optional) - For NVIDIA GPU detection
- `rocm-smi` (optional) - For AMD GPU detection
- `ollama` (optional) - For Ollama model management

---

## Version History

- **v1.0.0** - Initial model picker with GPU support
- **v1.1.0** - Added presets and Ollama integration
- **v1.2.0** - Added embedding model selection

---

## See Also

- `letta_integration/__init__.py` - Core Letta integration
- `save_memory.py` - Memory operations
- `setup_letta_agents.py` - Agent setup script
