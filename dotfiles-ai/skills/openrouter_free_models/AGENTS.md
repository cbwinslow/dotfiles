# OpenRouter Free Models - Agent Guide

## Overview

This skill provides three implementations (Python, Shell, TypeScript) for discovering, testing, and maintaining an active list of working free models on OpenRouter.

**Key insight**: OpenRouter lists ~28 free models, but many don't actually respond outside IDE context, are rate-limited, or return empty responses. Testing each model reveals which ones are truly available.

## Test Results (April 3, 2026)

### Summary
- **Total models on OpenRouter**: 351
- **Free models listed**: 28
- **Actually working (union of all runs)**: 22 unique models
- **Consistently failed**: 6 models (always return errors)

### Consistently Active Models (found in all 3 implementations)
| Model | Avg Response Time | Notes |
|-------|------------------|-------|
| `qwen/qwen3.6-plus:free` | ~900ms | Fast, reliable |
| `nvidia/nemotron-3-super-120b-a12b:free` | ~2000-8000ms | Large model, variable latency |
| `openrouter/free` | ~400-800ms | Router - picks random free model |
| `stepfun/step-3.5-flash:free` | ~1000-4000ms | Flash model, sometimes slow |

### Often Active (found in 2+ runs)
| Model | Avg Response Time | Notes |
|-------|------------------|-------|
| `arcee-ai/trinity-large-preview:free` | ~200-900ms | Very fast when available |
| `arcee-ai/trinity-mini:free` | ~140-2000ms | Fast, sometimes rate-limited |
| `google/gemma-3n-e4b-it:free` | ~300-400ms | Consistent performer |
| `google/gemma-3-4b-it:free` | ~900-1700ms | Slower but reliable |
| `liquid/lfm-2.5-1.2b-instruct:free` | ~140-600ms | Very fast |
| `liquid/lfm-2.5-1.2b-thinking:free` | ~200-300ms | Thinking model, fast |
| `minimax/minimax-m2.5:free` | ~500-3000ms | Variable latency |
| `nvidia/nemotron-3-nano-30b-a3b:free` | ~280-450ms | Fast, reliable |
| `nvidia/nemotron-nano-12b-v2-vl:free` | ~900-11000ms | Vision model, very slow sometimes |
| `openai/gpt-oss-120b:free` | ~700-1600ms | Good performance |
| `openai/gpt-oss-20b:free` | ~370-900ms | Fast OSS model |
| `z-ai/glm-4.5-air:free` | ~1300-7500ms | Sometimes times out |

### Intermittently Active (found in 1 run)
| Model | Notes |
|-------|-------|
| `google/gemma-3n-e2b-it:free` | Often 429 rate-limited |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | Venice provider |
| `meta-llama/llama-3.3-70b-instruct:free` | Large Llama model |
| `meta-llama/llama-3.2-3b-instruct:free` | Small Llama, slow sometimes |
| `nousresearch/hermes-3-llama-3.1-405b:free` | Huge model, very slow |
| `qwen/qwen3-coder:free` | Coding-focused, slow |
| `qwen/qwen3-next-80b-a3b-instruct:free` | Next-gen Qwen, slow |
| `nvidia/nemotron-nano-9b-v2:free` | Sometimes times out |

### Consistently Failed (never responded)
These models always returned errors (429, 500, or empty responses):
- Various deprecated or provider-restricted models

## Key Findings

### 1. Response Content Location
Many free models return responses in `reasoning` field instead of `content`:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "reasoning": "The user asks: Reply with exactly: P..."
    }
  }]
}
```
**All implementations now check both fields.**

### 2. Rate Limiting
- Free models share rate limits across the API key
- Running tests too frequently causes 429 errors
- Wait 15-30 seconds between full test runs
- Some models (like `gemma-3n-e2b-it`) are more aggressively rate-limited

### 3. Response Variability
- Same model can be fast one run and slow the next
- Provider routing changes dynamically
- `openrouter/free` router is the most reliable single endpoint

### 4. JSON Parsing Issues
- Some responses have leading whitespace before JSON
- Python's `aiohttp` `resp.json()` fails on whitespace-prefixed responses
- **Fix**: Read text, strip whitespace, then parse JSON manually

## Capabilities

### For AI Agents

#### 1. Dynamic Model Selection
```python
# Get current active models before making a request
manager = OpenRouterFreeModels(api_key)
await manager.refresh_all_models()
results = await manager.test_free_models()
best_model = min(results['active'], key=lambda m: m['response_time_ms'])
```

#### 2. Fallback Strategy
```python
# Try fastest model first, fall back to router
try:
    response = await call_model(best_model['model_id'])
except:
    response = await call_model('openrouter/free')
```

#### 3. Scheduled Testing
Run tests periodically to maintain fresh active list:
```bash
# Cron: test every hour
0 * * * * /path/to/openrouter_free_models.sh test
```

#### 4. Model Capability Discovery
Each implementation returns full model metadata:
- Context length
- Supported parameters (tools, temperature, etc.)
- Architecture info
- Input/output modalities

### For Applications

#### 1. Load Balancing
Distribute requests across all active free models:
```python
active_models = manager.get_active_free_models()
# Round-robin or random selection
model = random.choice(active_models)
```

#### 2. Performance Monitoring
Track response times over time to detect degradation:
```python
# Compare current vs cached response times
cached = manager.load_active_cache()
for model in active_models:
    cached_time = next((m['response_time_ms'] for m in cached['active_models'] if m['model_id'] == model['model_id']), None)
    if cached_time and model['response_time_ms'] > cached_time * 2:
        print(f"Warning: {model['model_id']} is 2x slower than before")
```

#### 3. IDE Integration Detection
Some models only work within IDE context. Testing outside IDE reveals which ones:
- Models that return 429: rate-limited for non-IDE usage
- Models that return empty content: may require specific headers
- Models that timeout: may be IDE-only

## Usage

### Quick Start
```bash
# Python
pip install aiohttp
python openrouter_free_models.py --refresh --test

# Shell
bash openrouter_free_models.sh refresh
bash openrouter_free_models.sh test

# TypeScript
npx ts-node openrouter_free_models.ts refresh
npx ts-node openrouter_free_models.ts test
```

### As Library
```python
from openrouter_free_models import OpenRouterFreeModels

manager = OpenRouterFreeModels(api_key="sk-or-...")
free_models = await manager.refresh_all_models()
results = await manager.test_free_models()
active = manager.get_active_free_models()
```

## Files
| File | Purpose |
|------|---------|
| `openrouter_free_models.py` | Python implementation (async, aiohttp) |
| `openrouter_free_models.sh` | Shell implementation (curl, jq) |
| `openrouter_free_models.ts` | TypeScript implementation (native fetch) |
| `SKILL.md` | Skill documentation for AI agents |
| `AGENTS.md` | This file - results and capabilities |

## Cache Location
All implementations cache to `~/.cache/openrouter/`:
- `all_models.json` - Full model list from API
- `active_free_models.json` - Currently working models
- `failed_free_models.json` - Models that failed testing
