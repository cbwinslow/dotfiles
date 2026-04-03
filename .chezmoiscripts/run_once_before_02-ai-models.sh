#!/usr/bin/env bash
# run_once_before_02-ai-models.sh
# Install Ollama and pull base AI models
set -euo pipefail

if command -v ollama &>/dev/null; then
    echo "==> Ollama already installed: $(ollama --version 2>/dev/null || echo 'installed')"
else
    echo "==> Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Wait for Ollama service to start
sleep 3

# Pull base models (idempotent - skips if already pulled)
MODELS=("nomic-embed-text" "llama3.1:8b")
for model in "${MODELS[@]}"; do
    if ollama list 2>/dev/null | grep -q "$model"; then
        echo "==> Model $model already available"
    else
        echo "==> Pulling model: $model"
        ollama pull "$model" || echo "==> WARNING: Failed to pull $model (non-fatal)"
    fi
done

echo "==> AI models setup complete."
