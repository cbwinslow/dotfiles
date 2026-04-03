#!/usr/bin/env python3
"""
OpenRouter Free Models Manager

Fetches all models from OpenRouter, filters for free models,
and tests each one to maintain an active list of working free models.

Usage:
    from openrouter_free_models import OpenRouterFreeModels

    manager = OpenRouterFreeModels(api_key="sk-or-...")
    await manager.refresh_all_models()
    await manager.test_free_models()
    active = manager.get_active_free_models()
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ModelInfo:
    id: str
    name: str
    context_length: int
    pricing_prompt: float
    pricing_completion: float
    architecture: dict
    top_provider: dict
    supported_parameters: list
    created: int
    description: str = ""
    hugging_face_id: Optional[str] = None


@dataclass
class ActiveFreeModel:
    model_id: str
    name: str
    context_length: int
    tested_at: float
    response_time_ms: float
    test_prompt: str = ""
    test_response: str = ""
    status: str = "active"


class OpenRouterFreeModels:
    BASE_URL = "https://openrouter.ai/api/v1"
    MODELS_ENDPOINT = f"{BASE_URL}/models"
    CHAT_ENDPOINT = f"{BASE_URL}/chat/completions"

    TEST_PROMPT = "Reply with exactly: PING"
    TEST_TIMEOUT = 30
    CONCURRENT_TESTS = 5

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_file: Optional[str] = None,
        active_cache_file: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set. Provide via constructor or environment variable."
            )

        cache_dir = Path.home() / ".cache" / "openrouter"
        cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = cache_file or str(cache_dir / "all_models.json")
        self.active_cache_file = active_cache_file or str(cache_dir / "active_free_models.json")

        self.all_models: list[ModelInfo] = []
        self.free_models: list[ModelInfo] = []
        self.active_free_models: list[ActiveFreeModel] = []
        self._last_refresh: float = 0
        self._last_test: float = 0

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/cbwinslow/dotfiles",
            "X-Title": "CBW OpenRouter Free Models",
        }

    async def _fetch_json(self, session, url: str, method: str = "GET", body: Optional[dict] = None) -> dict:
        kwargs = {
            "method": method,
            "url": url,
            "headers": self._headers(),
        }
        if body:
            kwargs["json"] = body

        async with session.request(**kwargs) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

    async def refresh_all_models(self) -> list[ModelInfo]:
        """Fetch all models from OpenRouter API and cache them."""
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.MODELS_ENDPOINT, headers=self._headers()) as resp:
                resp.raise_for_status()
                data = await resp.json()

        models_data = data.get("data", [])
        self.all_models = []

        for m in models_data:
            pricing = m.get("pricing", {})
            arch = m.get("architecture", {})
            top_prov = m.get("top_provider", {})

            model_info = ModelInfo(
                id=m["id"],
                name=m.get("name", m["id"]),
                context_length=m.get("context_length", 0),
                pricing_prompt=float(pricing.get("prompt", 0)),
                pricing_completion=float(pricing.get("completion", 0)),
                architecture=arch,
                top_provider=top_prov,
                supported_parameters=m.get("supported_parameters", []),
                created=m.get("created", 0),
                description=m.get("description", ""),
                hugging_face_id=m.get("hugging_face_id"),
            )
            self.all_models.append(model_info)

        self._filter_free_models()
        self._save_cache()
        self._last_refresh = time.time()

        return self.free_models

    def _filter_free_models(self):
        """Filter models where both prompt and completion pricing are 0."""
        self.free_models = [
            m for m in self.all_models
            if m.pricing_prompt == 0 and m.pricing_completion == 0
        ]

    def _save_cache(self):
        """Cache all models and free models to disk."""
        cache = {
            "refreshed_at": self._last_refresh,
            "total_models": len(self.all_models),
            "free_models_count": len(self.free_models),
            "free_models": [asdict(m) for m in self.free_models],
        }
        with open(self.cache_file, "w") as f:
            json.dump(cache, f, indent=2)

    def _save_active_cache(self):
        """Save active free models to disk."""
        cache = {
            "tested_at": self._last_test,
            "active_count": len(self.active_free_models),
            "failed_count": len(getattr(self, "_failed_models", [])),
            "active_models": [asdict(m) for m in self.active_free_models],
            "failed_models": getattr(self, "_failed_models", []),
        }
        with open(self.active_cache_file, "w") as f:
            json.dump(cache, f, indent=2)

    async def _test_single_model(self, session, model_id: str, name: str, context_length: int) -> Optional[ActiveFreeModel]:
        """Test a single free model with a simple chat completion."""
        start = time.time()
        try:
            async with session.post(
                self.CHAT_ENDPOINT,
                headers=self._headers(),
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": self.TEST_PROMPT}],
                    "max_tokens": 10,
                },
            ) as resp:
                elapsed_ms = (time.time() - start) * 1000

                if resp.status != 200:
                    return None

                text = await resp.text()
                text = text.strip()
                if not text:
                    return None

                data = json.loads(text)
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = message.get("content", "") or message.get("reasoning", "")

                if not content:
                    return None

                return ActiveFreeModel(
                    model_id=model_id,
                    name=name,
                    context_length=context_length,
                    tested_at=time.time(),
                    response_time_ms=round(elapsed_ms, 2),
                    test_prompt=self.TEST_PROMPT,
                    test_response=content[:200],
                    status="active",
                )
        except Exception:
            return None

    async def test_free_models(
        self,
        model_ids: Optional[list[str]] = None,
        max_concurrent: int = CONCURRENT_TESTS,
    ) -> dict:
        """
        Test all free models (or a subset) to see which are working.

        Args:
            model_ids: Specific model IDs to test. If None, tests all free models.
            max_concurrent: Max concurrent test requests.

        Returns:
            dict with 'active' and 'failed' model lists.
        """
        if not self.free_models:
            await self.refresh_all_models()

        targets = [m for m in self.free_models if not model_ids or m.id in model_ids]

        self.active_free_models = []
        self._failed_models = []

        import aiohttp
        timeout = aiohttp.ClientTimeout(total=self.TEST_TIMEOUT)
        connector = aiohttp.TCPConnector(limit=0, force_close=True)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def bounded_test(model: ModelInfo):
                async with semaphore:
                    return await self._test_single_model(session, model.id, model.name, model.context_length)

            tasks = [bounded_test(m) for m in targets]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception) or result is None:
                    continue
                if isinstance(result, ActiveFreeModel):
                    self.active_free_models.append(result)

            for m in targets:
                if not any(a.model_id == m.id for a in self.active_free_models):
                    self._failed_models.append({
                        "model_id": m.id,
                        "name": m.name,
                        "context_length": m.context_length,
                    })

        self._last_test = time.time()
        self._save_active_cache()

        return {
            "active": [asdict(m) for m in self.active_free_models],
            "failed": self._failed_models,
            "total_tested": len(targets),
            "active_count": len(self.active_free_models),
            "failed_count": len(self._failed_models),
        }

    def get_active_free_models(self) -> list[ActiveFreeModel]:
        """Return the current list of active free models."""
        return self.active_free_models

    def get_free_model_ids(self) -> list[str]:
        """Return IDs of all free models."""
        return [m.id for m in self.free_models]

    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """Look up a model by its ID."""
        for m in self.all_models:
            if m.id == model_id:
                return m
        return None

    def load_active_cache(self) -> dict:
        """Load previously cached active free models."""
        try:
            with open(self.active_cache_file) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_all_cache(self) -> dict:
        """Load previously cached all models."""
        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def summary(self) -> dict:
        """Print a summary of the current state."""
        return {
            "total_models": len(self.all_models),
            "free_models": len(self.free_models),
            "active_free_models": len(self.active_free_models),
            "last_refresh": time.ctime(self._last_refresh) if self._last_refresh else "never",
            "last_test": time.ctime(self._last_test) if self._last_test else "never",
        }


async def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenRouter Free Models Manager")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--refresh", action="store_true", help="Refresh all models from API")
    parser.add_argument("--test", action="store_true", help="Test all free models")
    parser.add_argument("--model", help="Test a specific model ID")
    parser.add_argument("--list", action="store_true", help="List free models")
    parser.add_argument("--active", action="store_true", help="Show active free models")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--concurrent", type=int, default=5, help="Max concurrent tests")
    args = parser.parse_args()

    try:
        manager = OpenRouterFreeModels(api_key=args.api_key)
    except ValueError as e:
        print(f"Error: {e}")
        return

    if args.refresh:
        print("Fetching all models from OpenRouter...")
        free = await manager.refresh_all_models()
        print(f"Found {len(free)} free models out of {len(manager.all_models)} total")

    if args.test:
        print("Testing all free models...")
        results = await manager.test_free_models(max_concurrent=args.concurrent)
        print(f"\nResults: {results['active_count']} active / {results['failed_count']} failed / {results['total_tested']} tested")
        if results["active"]:
            print("\nActive free models:")
            for m in results["active"]:
                print(f"  {m['model_id']} ({m['response_time_ms']}ms)")

    if args.model:
        print(f"Testing model: {args.model}")
        results = await manager.test_free_models(model_ids=[args.model])
        if results["active"]:
            m = results["active"][0]
            print(f"  ACTIVE: {m['model_id']} ({m['response_time_ms']}ms)")
            print(f"  Response: {m['test_response'][:100]}")
        else:
            print(f"  FAILED: {args.model}")

    if args.list:
        if not manager.free_models:
            cached = manager.load_all_cache()
            if cached.get("free_models"):
                print(f"Loaded {len(cached['free_models'])} free models from cache")
                for m in cached["free_models"]:
                    print(f"  {m['id']} - {m['name']} (ctx: {m['context_length']})")
            else:
                print("No models cached. Run --refresh first.")
        else:
            print(f"Free models ({len(manager.free_models)}):")
            for m in manager.free_models:
                print(f"  {m.id} - {m.name} (ctx: {m.context_length})")

    if args.active:
        cached = manager.load_active_cache()
        if cached.get("active_models"):
            print(f"Active free models ({cached['active_count']}):")
            for m in cached["active_models"]:
                print(f"  {m['model_id']} - {m['name']} ({m['response_time_ms']}ms)")
        else:
            print("No active models cached. Run --test first.")

    if args.summary:
        s = manager.summary()
        print(json.dumps(s, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
