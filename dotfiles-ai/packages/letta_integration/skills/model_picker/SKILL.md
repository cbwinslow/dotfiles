# Model Picker Skill (Letta)

Configure GPU models for Letta agents.

**Version**: 1.0.0  
**Location**: `~/dotfiles/ai/packages/letta_integration/letta_model_picker.py`

## Quick Start

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

# Use Ollama (simplest)
letta.configure_models(
    llm_model="llama3.1:8b",
    embedding_model="bge-m3:latest",
    use_ollama=True
)

# Or use GPU llama.cpp
letta.configure_models(
    model_path="/models/llama-3-8b.Q4_K_M.gguf",
    n_gpu_layers=35
)
```

## Presets

```python
letta.apply_model_preset("fast_gpu")      # 35 GPU layers
letta.apply_model_preset("quality_gpu")   # 99 GPU layers  
letta.apply_model_preset("cpu_fallback")  # No GPU
letta.apply_model_preset("ollama_standard")  # Ollama
```

## GPU Layers Guide

| VRAM | Layers | Preset |
|------|--------|--------|
| 8GB  | 20     | conservative |
| 12GB | 35     | default |
| 16GB | 45     | high |
| 24GB | 99     | all layers |

## Check Configuration

```python
info = letta.get_current_model_info()
print(f"Model: {info['llm']['model_name']}")
print(f"Embedding: {info['embedding']['model_name']}")
print(f"GPU: {info['hardware']['gpu_available']}")
```

## Embeddings

- **bge-m3:latest** - 1024 dims, higher quality
- **nomic-embed-text:latest** - 768 dims, faster

## Simple Direct Usage

```python
from letta_model_picker import ModelPicker

picker = ModelPicker()
picker.apply_preset("ollama_standard")
config = picker.to_letta_agent_config()
# config has 'model' and 'embedding' ready for Letta
```

# Check current configuration
letta.print_model_info()
```

### 2. Using Model Presets

```python
# Apply preset configuration
letta.apply_model_preset("fast_gpu")

# Available presets:
# - fast_gpu: Fast inference with GPU (35 layers)
# - quality_gpu: High quality with full GPU (99 layers)
# - cpu_fallback: CPU-only (no GPU)
# - ollama_standard: Standard Ollama setup
# - letta_free: Letta's built-in free model

# Then set model path for GPU presets
letta.model_picker.llm_config.model_path = "/path/to/model.gguf"

# Create agent
config = letta.model_picker.to_letta_agent_config()
agent = letta.create_agent_with_config("myagent", config)
```

### 3. Using Ollama

```python
# Configure Ollama models
letta.configure_models(
    llm_model="llama3.1:8b",
    embedding_model="bge-m3:latest",
    use_ollama=True
)

# Or apply Ollama preset
letta.apply_model_preset("ollama_standard")
```

---

## Core Operations

### GPU Configuration Guide

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

# Configure based on available VRAM

# 8GB VRAM
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=20  # Conservative for 8GB
)

# 12GB VRAM (current default)
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

# 16GB VRAM
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=45
)

# 24GB+ VRAM (all layers on GPU)
letta.configure_models(
    model_path="/models/llama-3-70b-instruct.Q4_K_M.gguf",
    n_gpu_layers=99
)
```

### Embedding Model Selection

```python
# High quality (BGE-M3, 1024 dimensions)
letta.configure_models(
    llm_model="llama3.1:8b",
    embedding_model="bge-m3:latest",  # Best quality
    use_ollama=True
)

# Fast (Nomic, 768 dimensions)
letta.configure_models(
    llm_model="llama3.1:8b",
    embedding_model="nomic-embed-text:latest",  # Faster
    use_ollama=True
)
```

### Direct Model Picker Usage

```python
from letta_model_picker import ModelPicker, create_gpu_config, create_ollama_config

# Method 1: ModelPicker class
picker = ModelPicker()
picker.configure_gpu_llama(
    model_path="/models/model.gguf",
    n_gpu_layers=35
)
llm_config, embedding_config = picker.get_config()

# Method 2: Quick GPU config
llm_config, embedding_config = create_gpu_config(
    model_path="/models/model.gguf",
    n_gpu_layers=35,
    embedding_model="nomic-embed-text:latest"
)

# Method 3: Quick Ollama config
llm_config, embedding_config = create_ollama_config(
    llm_model="llama3.1:8b",
    embedding_model="bge-m3:latest"
)
```

---

## Supported Model Providers

| Provider | GPU Support | Use Case | Configuration |
|----------|-------------|----------|---------------|
| **llama.cpp** | ✅ NVIDIA/AMD | Fast local inference | `model_path`, `n_gpu_layers` |
| **Ollama** | ✅ GPU | Easy model management | `llm_model`, `embedding_model` |
| **OpenRouter** | ❌ | Many models, API-based | `model_name`, `api_key` |
| **Letta Free** | ❌ | Always available | Built-in fallback |

---

## Supported Embedding Providers

| Provider | Model | Dimensions | Speed | Best For |
|----------|-------|------------|-------|----------|
| **BGE-M3** | bge-m3:latest | 1024 | Medium | High quality RAG |
| **Nomic** | nomic-embed-text:latest | 768 | Fast | Speed-critical apps |
| **Ollama** | Various | Varies | Medium | Flexibility |

---

## Advanced Features

### 1. Multi-GPU Configuration

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

### 2. GPU Detection

```python
from letta_model_picker import ModelPicker

picker = ModelPicker()

# Check GPU availability
print(f"GPU Available: {picker.gpu_available}")

# Get detailed info
info = picker.get_gpu_info()
print(f"Devices: {info['devices']}")
print(f"Driver: {info['driver_version']}")
print(f"CUDA: {info['cuda_version']}")
```

### 3. Model Information for Agents

```python
# Get detailed model info
info = letta.get_current_model_info()

print(f"""
Model Configuration:
- LLM: {info['llm']['model_name']} ({info['llm']['provider']})
- Context: {info['llm']['context_length']} tokens
- Temperature: {info['llm']['temperature']}
- GPU: {'Enabled' if info['llm']['using_gpu'] else 'Disabled'}
- GPU Layers: {info['llm']['gpu_layers']}

Embedding:
- Model: {info['embedding']['model_name']}
- Provider: {info['embedding']['provider']}
- Dimensions: {info['embedding']['dimensions']}

Hardware:
- GPU Available: {info['hardware']['gpu_available']}
- Devices: {len(info['hardware']['gpu_info']['devices'])}

Recommended For:
{chr(10).join(['  • ' + use for use in info['recommended_for']])}
""")
```

---

## Configuration Classes

### LLMConfig

```python
from letta_model_picker import LLMConfig, ModelProvider, GPUConfig

config = LLMConfig(
    provider=ModelProvider.LLAMA_CPP,
    model_name="llama-3-8b-instruct",
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    context_length=8192,
    temperature=0.7,
    top_p=0.9,
    max_tokens=2048,
    gpu_config=GPUConfig(
        enabled=True,
        n_gpu_layers=35,
        main_gpu=0
    )
)
```

### EmbeddingConfig

```python
from letta_model_picker import EmbeddingConfig, EmbeddingProvider

config = EmbeddingConfig(
    provider=EmbeddingProvider.BGE_M3,
    model_name="bge-m3:latest",
    dimensions=1024,
    normalize=True,
    batch_size=32
)
```

---

## Model Presets

### Available Presets

```python
from letta_model_picker import ModelPicker

picker = ModelPicker()

# List all presets
for preset in picker.list_presets():
    print(f"{preset['name']}: {preset['description']}")
```

| Preset | Description | LLM | Embedding | GPU Layers |
|--------|-------------|-----|-----------|------------|
| **fast_gpu** | Fast inference | llama.cpp | nomic-embed-text | 35 |
| **quality_gpu** | High quality | llama.cpp | bge-m3 | 99 |
| **cpu_fallback** | CPU only | Ollama | nomic-embed-text | 0 |
| **ollama_standard** | Standard setup | Ollama | bge-m3 | Auto |
| **letta_free** | Free tier | letta-free | bge-m3 | None |

### Applying Presets

```python
# Apply preset
picker.apply_preset("fast_gpu")

# Override model path
picker.llm_config.model_path = "/path/to/model.gguf"

# Override GPU layers
picker.llm_config.gpu_config.n_gpu_layers = 40
```

---

## Integration with Letta

### Creating Agents with Custom Models

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

# Step 1: Configure models
config = letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35,
    embedding_model="bge-m3:latest"
)

# Step 2: Create agent with config
result = letta.create_agent_with_config("myagent", config)
print(f"Agent created: {result['id']}")

# Step 3: Setup core memory
letta.setup_core_memory_blocks(
    persona_value="I am an AI assistant with GPU acceleration...",
    human_value="User is a software developer..."
)
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
    letta.create_agent_with_config("myagent", config)
```

---

## Best Practices

### 1. Always Check GPU Availability

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="windsurf")

if letta.model_picker and letta.model_picker.gpu_available:
    # Use GPU configuration
    letta.configure_models(n_gpu_layers=35)
else:
    # Use CPU fallback
    letta.apply_model_preset("cpu_fallback")
```

### 2. Use Appropriate GPU Layers

```python
# Match n_gpu_layers to available VRAM
vram_gb = 12  # Detected or configured

if vram_gb >= 24:
    n_layers = 99  # All on GPU
elif vram_gb >= 16:
    n_layers = 45
elif vram_gb >= 12:
    n_layers = 35
elif vram_gb >= 8:
    n_layers = 20
else:
    n_layers = 0  # CPU only

letta.configure_models(n_gpu_layers=n_layers)
```

### 3. Log Model Configuration

```python
# Always log what models are being used
info = letta.get_current_model_info()
letta._save_to_memory(
    content=f"Using {info['llm']['model_name']} with {info['llm']['gpu_layers']} GPU layers",
    memory_type="context",
    tags=["model_config", info['llm']['provider']]
)
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
    def get_gpu_info() -> Dict
    def print_config()
```

### LettaIntegration Model Methods

```python
class LettaIntegration:
    def configure_models(model_path, n_gpu_layers, llm_model, ...)
    def create_agent_with_config(agent_name, model_config)
    def get_current_model_info()
    def print_model_info()
    def apply_model_preset(preset_name)
```

### Convenience Functions

```python
def create_gpu_config(model_path, n_gpu_layers, embedding_model)
def create_ollama_config(llm_model, embedding_model)
def get_current_models()
```

---

## Troubleshooting

### Common Issues

1. **GPU Not Detected**
   ```bash
   # Check GPU manually
   nvidia-smi  # NVIDIA
   rocm-smi    # AMD
   ```

2. **Model File Not Found**
   ```python
   import os
   if not os.path.exists(model_path):
       print(f"Model not found: {model_path}")
       # Use Ollama fallback
       letta.configure_models(use_ollama=True)
   ```

3. **Out of Memory**
   ```python
   # Reduce GPU layers
   letta.configure_models(n_gpu_layers=20)  # From 35
   
   # Or use CPU fallback
   letta.apply_model_preset("cpu_fallback")
   ```

### Debug Commands

```bash
# Check GPU
python3 -c "from letta_model_picker import ModelPicker; p = ModelPicker(); print(p.get_gpu_info())"

# Test model picker
python3 -c "from letta_model_picker import ModelPicker; p = ModelPicker(); p.print_config()"

# Check Letta models
curl http://localhost:8283/v1/models
```

---

## Examples

### Example 1: Complete GPU Setup

```python
import sys
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/packages/letta_integration')
from letta_integration import LettaIntegration

# Initialize
letta = LettaIntegration(agent_name="windsurf")

# Check GPU
if letta.model_picker and letta.model_picker.gpu_available:
    # Configure for GPU
    letta.configure_models(
        model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
        n_gpu_layers=35,
        embedding_model="nomic-embed-text:latest"  # Fast for testing
    )
    print("✓ GPU configuration applied")
else:
    letta.apply_model_preset("ollama_standard")
    print("✓ Ollama configuration applied")

# Show configuration
letta.print_model_info()

# Create agent
config = letta.model_picker.to_letta_agent_config()
agent = letta.create_agent_with_config("windsurf_gpu", config)

# Save configuration to memory
letta._save_to_memory(
    content=f"Agent created with {config}",
    memory_type="context",
    tags=["agent_creation", "model_config"]
)
```

### Example 2: Model Comparison

```python
from letta_model_picker import ModelPicker

models_to_test = [
    ("fast_gpu", "Quick tasks"),
    ("quality_gpu", "Complex reasoning"),
    ("ollama_standard", "General use")
]

picker = ModelPicker()

for preset, use_case in models_to_test:
    picker.apply_preset(preset)
    info = picker.get_model_info()
    
    print(f"\n{preset} ({use_case}):")
    print(f"  LLM: {info['llm']['model_name']}")
    print(f"  Embedding: {info['embedding']['model_name']}")
    print(f"  GPU: {info['llm']['using_gpu']}")
```

### Example 3: Multi-Model Agent

```python
from letta_integration import LettaIntegration

letta = LettaIntegration(agent_name="multi_model")

# Create multiple agents with different models

# Agent 1: Fast GPU for quick tasks
letta.configure_models(
    model_path="/models/llama-3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)
fast_config = letta.model_picker.to_letta_agent_config()
fast_agent = letta.create_agent_with_config("fast_agent", fast_config)

# Agent 2: Quality GPU for complex tasks
letta.apply_model_preset("quality_gpu")
letta.model_picker.llm_config.model_path = "/models/llama-3-70b-instruct.Q4_K_M.gguf"
quality_config = letta.model_picker.to_letta_agent_config()
quality_agent = letta.create_agent_with_config("quality_agent", quality_config)

print("Created fast and quality agents with different GPU configurations")
```

---

## Environment Variables

```bash
# Letta server
export LETTA_SERVER_URL="http://localhost:8283"
export LETTA_API_KEY="your-api-key"

# Ollama
export OLLAMA_HOST="http://localhost:11434"

# OpenRouter (if using)
export OPENROUTER_API_KEY="your-key"

# llama.cpp (if using)
export LLAMA_CPP_HOST="http://localhost:8080"
```

---

## Version History

- **1.0.0** (2026-03-28): Initial release
  - GPU llama.cpp support
  - Model picker with presets
  - Embedding model selection
  - Hardware detection

---

## See Also

- `conversation_logger/SKILL.md` - Automatic conversation logging
- `memory/SKILL.md` - Core memory management
- `~/dotfiles/ai/base/base_agent.yaml` - Default model configuration
