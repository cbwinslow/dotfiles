# OpenRouter Free Models Manager

Fetch all models from OpenRouter API, filter for free models, and test each one to maintain an active list of working free models. Some free models don't work outside IDE context -- this tool identifies which ones are actually responding.

## Overview

Three implementations (Python, Shell, TypeScript) that:

1. **Fetch** all models from `GET /api/v1/models`
2. **Filter** for free models (pricing.prompt == 0 AND pricing.completion == 0)
3. **Test** each free model with a minimal chat completion to verify it responds
4. **Cache** results to `~/.cache/openrouter/` for reuse

## Files

| File | Language | Description |
|------|----------|-------------|
| `openrouter_free_models.py` | Python 3.9+ | Async class with CLI (`aiohttp`) |
| `openrouter_free_models.sh` | Bash 4+ | Functions + CLI (`curl` + `jq`) |
| `openrouter_free_models.ts` | TypeScript/Node | Class with CLI (native `fetch`) |

## Dependencies

### Python
```bash
pip install aiohttp
```

### Shell
```bash
# Requires: curl, jq, flock (usually pre-installed)
sudo apt install curl jq util-linux  # Debian/Ubuntu
```

### TypeScript
```bash
# No external deps needed (uses native fetch in Node 18+)
# For older Node: npm install node-fetch
```

## Usage

### Python

```python
from openrouter_free_models import OpenRouterFreeModels
import asyncio

async def main():
    manager = OpenRouterFreeModels(api_key="sk-or-...")

    # Fetch all models and filter free ones
    free_models = await manager.refresh_all_models()
    print(f"Found {len(free_models)} free models")

    # Test all free models to find which are actually working
    results = await manager.test_free_models()
    print(f"{results['active_count']} active / {results['failed_count']} failed")

    # Get active models
    active = manager.get_active_free_models()
    for m in active:
        print(f"  {m.model_id} ({m.response_time_ms}ms)")

    # Test a specific model
    results = await manager.test_free_models(model_ids=["meta-llama/llama-3.2-3b-instruct:free"])

asyncio.run(main())
```

CLI:
```bash
python openrouter_free_models.py --refresh --api-key sk-or-...
python openrouter_free_models.py --test --concurrent 10
python openrouter_free_models.py --list
python openrouter_free_models.py --active
python openrouter_free_models.py --model "google/gemma-3-4b-it:free"
python openrouter_free_models.py --summary
```

### Shell

```bash
# Source the file to use functions interactively
source openrouter_free_models.sh

# Or run directly
bash openrouter_free_models.sh refresh sk-or-...
bash openrouter_free_models.sh list
bash openrouter_free_models.sh test
bash openrouter_free_models.sh test-single "meta-llama/llama-3.2-3b-instruct:free"
bash openrouter_free_models.sh active
bash openrouter_free_models.sh summary
```

Environment variables:
```bash
export OPENROUTER_API_KEY="sk-or-..."
export OR_CONCURRENT=10    # Max concurrent tests (default: 5)
export OR_TEST_TIMEOUT=30  # Timeout per test in seconds (default: 30)
```

### TypeScript

```typescript
import { OpenRouterFreeModels } from './openrouter_free_models';

const manager = new OpenRouterFreeModels(); // reads OPENROUTER_API_KEY from env

// Fetch all models
const freeModels = await manager.refreshAllModels();
console.log(`Found ${freeModels.length} free models`);

// Test all free models
const results = await manager.testFreeModels();
console.log(`${results.active_count} active / ${results.failed_count} failed`);

// Get active models
const active = manager.getActiveFreeModels();
for (const m of active) {
  console.log(`  ${m.model_id} (${m.response_time_ms}ms)`);
}

// Test specific models
const results = await manager.testFreeModels({
  modelIds: ['meta-llama/llama-3.2-3b-instruct:free'],
  maxConcurrent: 10,
});
```

CLI:
```bash
node openrouter_free_models.ts refresh --api-key sk-or-...
node openrouter_free_models.ts test --concurrent 10
node openrouter_free_models.ts list
node openrouter_free_models.ts active
node openrouter_free_models.ts test-single "google/gemma-3-4b-it:free"
node openrouter_free_models.ts summary
```

## How It Works

1. **List Models**: Calls `GET https://openrouter.ai/api/v1/models` with API key
2. **Filter Free**: Keeps models where `pricing.prompt == 0` AND `pricing.completion == 0`
3. **Test Each**: Sends `POST /api/v1/chat/completions` with `{"model": "<id>", "messages": [{"role": "user", "content": "Reply with exactly: PING"}], "max_tokens": 10}`
4. **Track Results**: HTTP 200 = active, anything else = failed
5. **Cache**: Saves results to `~/.cache/openrouter/` for reuse

## Why Test?

OpenRouter's free model list includes models that:
- May be temporarily unavailable
- Only work within specific IDE integrations
- Have been deprecated but still listed
- Have rate limits that make them effectively unusable

Testing ensures you only route to models that actually respond.

## Cache Files

| File | Contents |
|------|----------|
| `~/.cache/openrouter/all_models.json` | All models from API |
| `~/.cache/openrouter/free_models.json` | Filtered free models |
| `~/.cache/openrouter/active_free_models.json` | Tested working models |
| `~/.cache/openrouter/failed_free_models.json` | Tested failed models |
