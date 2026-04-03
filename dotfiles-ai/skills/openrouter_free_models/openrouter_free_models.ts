/**
 * OpenRouter Free Models Manager (TypeScript)
 *
 * Fetches all models from OpenRouter, filters free models,
 * and tests each one to maintain an active list of working free models.
 *
 * Usage:
 *   import { OpenRouterFreeModels } from './openrouter_free_models';
 *
 *   const manager = new OpenRouterFreeModels();
 *   await manager.refreshAllModels();
 *   await manager.testFreeModels();
 *   const active = manager.getActiveFreeModels();
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface ModelInfo {
  id: string;
  name: string;
  context_length: number;
  pricing_prompt: number;
  pricing_completion: number;
  architecture: Record<string, unknown>;
  top_provider: Record<string, unknown>;
  supported_parameters: string[];
  created: number;
  description?: string;
  hugging_face_id?: string | null;
}

export interface ActiveFreeModel {
  model_id: string;
  name: string;
  context_length: number;
  tested_at: number;
  response_time_ms: number;
  test_prompt: string;
  test_response: string;
  status: 'active' | 'failed';
}

export interface FailedModel {
  model_id: string;
  name: string;
  context_length: number;
  http_code?: string;
  error?: string;
}

export interface TestResults {
  active: ActiveFreeModel[];
  failed: FailedModel[];
  total_tested: number;
  active_count: number;
  failed_count: number;
}

export interface ModelSummary {
  total_models: number;
  free_models: number;
  active_free_models: number;
  last_refresh: string;
  last_test: string;
}

export class OpenRouterFreeModels {
  private static readonly BASE_URL = 'https://openrouter.ai/api/v1';
  private static readonly MODELS_ENDPOINT = `${OpenRouterFreeModels.BASE_URL}/models`;
  private static readonly CHAT_ENDPOINT = `${OpenRouterFreeModels.BASE_URL}/chat/completions`;
  private static readonly TEST_PROMPT = 'Reply with exactly: PING';
  private static readonly TEST_TIMEOUT = 30000;
  private static readonly CONCURRENT_TESTS = 5;

  private apiKey: string;
  cacheFile: string;
  activeCacheFile: string;
  failedCacheFile: string;

  allModels: ModelInfo[] = [];
  freeModels: ModelInfo[] = [];
  activeFreeModels: ActiveFreeModel[] = [];
  failedModels: FailedModel[] = [];

  private lastRefresh = 0;
  private lastTest = 0;

  constructor(apiKey?: string, cacheDir?: string) {
    this.apiKey = apiKey || process.env.OPENROUTER_API_KEY || '';
    if (!this.apiKey) {
      throw new Error(
        'OPENROUTER_API_KEY not set. Provide via constructor or environment variable.'
      );
    }

    const defaultCacheDir = path.join(os.homedir(), '.cache', 'openrouter');
    const dir = cacheDir || defaultCacheDir;

    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    this.cacheFile = path.join(dir, 'all_models.json');
    this.activeCacheFile = path.join(dir, 'active_free_models.json');
    this.failedCacheFile = path.join(dir, 'failed_free_models.json');
  }

  private getHeaders(): Record<string, string> {
    return {
      Authorization: `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://github.com/cbwinslow/dotfiles',
      'X-Title': 'CBW OpenRouter Free Models',
    };
  }

  private async fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), OpenRouterFreeModels.TEST_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return (await response.json()) as T;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async refreshAllModels(): Promise<ModelInfo[]> {
    interface ModelsResponse {
      data: Array<{
        id: string;
        name: string;
        context_length: number;
        pricing: { prompt: string | number; completion: string | number; [key: string]: unknown };
        architecture: Record<string, unknown>;
        top_provider: Record<string, unknown>;
        supported_parameters: string[];
        created: number;
        description?: string;
        hugging_face_id?: string | null;
        [key: string]: unknown;
      }>;
    }

    const data = await this.fetchJson<ModelsResponse>(OpenRouterFreeModels.MODELS_ENDPOINT, {
      headers: this.getHeaders(),
    });

    this.allModels = data.data.map((m) => ({
      id: m.id,
      name: m.name || m.id,
      context_length: m.context_length || 0,
      pricing_prompt: Number(m.pricing?.prompt || 0),
      pricing_completion: Number(m.pricing?.completion || 0),
      architecture: m.architecture || {},
      top_provider: m.top_provider || {},
      supported_parameters: m.supported_parameters || [],
      created: m.created || 0,
      description: m.description || '',
      hugging_face_id: m.hugging_face_id || null,
    }));

    this.filterFreeModels();
    this.saveCache();
    this.lastRefresh = Date.now();

    return this.freeModels;
  }

  private filterFreeModels(): void {
    this.freeModels = this.allModels.filter(
      (m) => m.pricing_prompt === 0 && m.pricing_completion === 0
    );
  }

  private saveCache(): void {
    const cache = {
      refreshed_at: this.lastRefresh,
      total_models: this.allModels.length,
      free_models_count: this.freeModels.length,
      free_models: this.freeModels,
    };
    fs.writeFileSync(this.cacheFile, JSON.stringify(cache, null, 2));
  }

  private saveActiveCache(): void {
    const cache = {
      tested_at: this.lastTest,
      active_count: this.activeFreeModels.length,
      failed_count: this.failedModels.length,
      active_models: this.activeFreeModels,
      failed_models: this.failedModels,
    };
    fs.writeFileSync(this.activeCacheFile, JSON.stringify(cache.active_models, null, 2));
    fs.writeFileSync(this.failedCacheFile, JSON.stringify(cache.failed_models, null, 2));
  }

  private async testSingleModel(
    modelId: string,
    name: string,
    contextLength: number
  ): Promise<ActiveFreeModel | null> {
    const startTime = Date.now();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), OpenRouterFreeModels.TEST_TIMEOUT);

      const response = await fetch(OpenRouterFreeModels.CHAT_ENDPOINT, {
        method: 'POST',
        headers: this.getHeaders(),
        signal: controller.signal,
        body: JSON.stringify({
          model: modelId,
          messages: [{ role: 'user', content: OpenRouterFreeModels.TEST_PROMPT }],
          max_tokens: 10,
        }),
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        return null;
      }

      const data = (await response.json()) as {
        choices: Array<{ message: { content: string } }>;
      };

      const elapsedMs = Date.now() - startTime;
      const choice = data.choices?.[0];
      const message = choice?.message as Record<string, unknown> | undefined;
      const content = (message?.content as string) || (message?.reasoning as string) || '';

      return {
        model_id: modelId,
        name,
        context_length: contextLength,
        tested_at: Date.now(),
        response_time_ms: Math.round(elapsedMs * 100) / 100,
        test_prompt: OpenRouterFreeModels.TEST_PROMPT,
        test_response: content.substring(0, 200),
        status: 'active',
      };
    } catch {
      return null;
    }
  }

  async testFreeModels(options?: {
    modelIds?: string[];
    maxConcurrent?: number;
  }): Promise<TestResults> {
    if (this.freeModels.length === 0) {
      await this.refreshAllModels();
    }

    const targets = options?.modelIds
      ? this.freeModels.filter((m) => options.modelIds!.includes(m.id))
      : [...this.freeModels];

    const maxConcurrent = options?.maxConcurrent ?? OpenRouterFreeModels.CONCURRENT_TESTS;

    this.activeFreeModels = [];
    this.failedModels = [];

    // Process with concurrency control
    const results: (ActiveFreeModel | null)[] = [];
    const queue = [...targets];

    const worker = async () => {
      while (queue.length > 0) {
        const model = queue.shift()!;
        const result = await this.testSingleModel(model.id, model.name, model.context_length);
        results.push(result);
      }
    };

    const workers = Array.from({ length: Math.min(maxConcurrent, targets.length) }, () => worker());
    await Promise.all(workers);

    for (let i = 0; i < targets.length; i++) {
      const model = targets[i];
      const result = results[i];

      if (result) {
        this.activeFreeModels.push(result);
      } else {
        this.failedModels.push({
          model_id: model.id,
          name: model.name,
          context_length: model.context_length,
        });
      }
    }

    this.lastTest = Date.now();
    this.saveActiveCache();

    return {
      active: this.activeFreeModels,
      failed: this.failedModels,
      total_tested: targets.length,
      active_count: this.activeFreeModels.length,
      failed_count: this.failedModels.length,
    };
  }

  getActiveFreeModels(): ActiveFreeModel[] {
    return this.activeFreeModels;
  }

  getFreeModelIds(): string[] {
    return this.freeModels.map((m) => m.id);
  }

  getModelById(modelId: string): ModelInfo | undefined {
    return this.allModels.find((m) => m.id === modelId);
  }

  loadActiveCache(): Record<string, unknown> {
    try {
      const data = fs.readFileSync(this.activeCacheFile, 'utf-8');
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  loadAllCache(): Record<string, unknown> {
    try {
      const data = fs.readFileSync(this.cacheFile, 'utf-8');
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  summary(): ModelSummary {
    return {
      total_models: this.allModels.length,
      free_models: this.freeModels.length,
      active_free_models: this.activeFreeModels.length,
      last_refresh: this.lastRefresh ? new Date(this.lastRefresh).toISOString() : 'never',
      last_test: this.lastTest ? new Date(this.lastTest).toISOString() : 'never',
    };
  }
}

// CLI entry point
const isMainModule = (() => {
  if (typeof process !== 'undefined' && process.argv) {
    const scriptPath = process.argv[1] || '';
    return scriptPath.endsWith('openrouter_free_models.ts') || scriptPath.endsWith('openrouter_free_models.js');
  }
  return false;
})();

if (isMainModule) {
  const args = process.argv.slice(2);
  const command = args[0];

  const getApiKey = (): string | undefined => {
    const apiKeyIdx = args.indexOf('--api-key');
    if (apiKeyIdx !== -1 && args[apiKeyIdx + 1]) {
      return args[apiKeyIdx + 1];
    }
    return process.env.OPENROUTER_API_KEY;
  };

  const run = async () => {
    const apiKey = getApiKey();
    if (!apiKey) {
      console.error('Error: OPENROUTER_API_KEY not set. Provide via --api-key or environment variable.');
      process.exit(1);
    }

    const manager = new OpenRouterFreeModels(apiKey);

    switch (command) {
      case 'refresh': {
        console.log('Fetching all models from OpenRouter...');
        const free = await manager.refreshAllModels();
        console.log(`Found ${free.length} free models out of ${manager.allModels.length} total`);
        break;
      }

      case 'list': {
        const cached = manager.loadAllCache();
        if (cached.free_models_count && (cached as any).free_models) {
          const freeModels = (cached as any).free_models as ModelInfo[];
          console.log(`Free models (${freeModels.length}):`);
          for (const m of freeModels) {
            console.log(`  ${m.id} - ${m.name} (context: ${m.context_length})`);
          }
        } else {
          console.log('No models cached. Run "refresh" first.');
        }
        break;
      }

      case 'test': {
        const concurrentIdx = args.indexOf('--concurrent');
        const maxConcurrent = concurrentIdx !== -1 && args[concurrentIdx + 1]
          ? parseInt(args[concurrentIdx + 1], 10)
          : undefined;

        console.log('Testing all free models...');
        const results = await manager.testFreeModels({ maxConcurrent });
        console.log(
          `\nResults: ${results.active_count} active / ${results.failed_count} failed / ${results.total_tested} tested`
        );
        if (results.active.length > 0) {
          console.log('\nActive free models:');
          for (const m of results.active) {
            console.log(`  ${m.model_id} (${m.response_time_ms}ms)`);
          }
        }
        break;
      }

      case 'test-single': {
        const modelId = args[1];
        if (!modelId) {
          console.error('Usage: node openrouter_free_models.ts test-single <model_id>');
          process.exit(1);
        }
        console.log(`Testing model: ${modelId}`);
        const results = await manager.testFreeModels({ modelIds: [modelId] });
        if (results.active.length > 0) {
          const m = results.active[0];
          console.log(`  ACTIVE: ${m.model_id} (${m.response_time_ms}ms)`);
          console.log(`  Response: ${m.test_response.substring(0, 100)}`);
        } else {
          console.log(`  FAILED: ${modelId}`);
        }
        break;
      }

      case 'active': {
        try {
          const data = fs.readFileSync(manager.activeCacheFile, 'utf-8');
          const models = JSON.parse(data) as ActiveFreeModel[];
          console.log(`Active free models (${models.length}):`);
          for (const m of models) {
            console.log(`  ${m.model_id} - ${m.name} (${m.response_time_ms}ms)`);
          }
        } catch {
          console.log('No active models cached. Run "test" first.');
        }
        break;
      }

      case 'summary': {
        const s = manager.summary();
        console.log(JSON.stringify(s, null, 2));
        break;
      }

      default:
        console.log(`Usage: node openrouter_free_models.ts {refresh|list|test|test-single <model_id>|active|summary} [--api-key <key>] [--concurrent <n>]`);
        process.exit(1);
    }
  };

  run().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
