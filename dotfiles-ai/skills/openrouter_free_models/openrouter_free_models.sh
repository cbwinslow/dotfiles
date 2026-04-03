#!/usr/bin/env bash
#
# OpenRouter Free Models Manager (Shell)
#
# Fetches all models, filters free ones, and tests them to maintain
# an active list of working free models.
#
# Usage:
#   source openrouter_free_models.sh
#   or_free_models_init                    # Initialize with API key
#   or_free_models_refresh                 # Fetch all models
#   or_free_models_list                    # List free models
#   or_free_models_test                    # Test all free models
#   or_free_models_test_single <model_id>  # Test a specific model
#   or_free_models_active                  # Show active free models
#   or_free_models_summary                 # Show summary
#
# Environment:
#   OPENROUTER_API_KEY - Your OpenRouter API key
#   OR_CONCURRENT - Max concurrent test requests (default: 5)
#   OR_TEST_TIMEOUT - Timeout per test in seconds (default: 30)
#   OR_CACHE_DIR - Cache directory (default: ~/.cache/openrouter)

OR_BASE_URL="https://openrouter.ai/api/v1"
OR_MODELS_URL="${OR_BASE_URL}/models"
OR_CHAT_URL="${OR_BASE_URL}/chat/completions"
OR_TEST_PROMPT="Reply with exactly: PING"
OR_CONCURRENT="${OR_CONCURRENT:-5}"
OR_TEST_TIMEOUT="${OR_TEST_TIMEOUT:-30}"
OR_CACHE_DIR="${OR_CACHE_DIR:-$HOME/.cache/openrouter}"
OR_ALL_MODELS_CACHE="${OR_CACHE_DIR}/all_models.json"
OR_FREE_MODELS_CACHE="${OR_CACHE_DIR}/free_models.json"
OR_ACTIVE_MODELS_CACHE="${OR_CACHE_DIR}/active_free_models.json"
OR_FAILED_MODELS_CACHE="${OR_CACHE_DIR}/failed_free_models.json"

# Internal state
_OR_API_KEY=""
_OR_ALL_MODELS_JSON=""
_OR_FREE_MODELS_JSON=""

or_free_models_init() {
    local api_key="${1:-$OPENROUTER_API_KEY}"
    if [[ -z "$api_key" ]]; then
        echo "Error: OPENROUTER_API_KEY not set. Provide via argument or environment variable." >&2
        return 1
    fi
    _OR_API_KEY="$api_key"
    mkdir -p "$OR_CACHE_DIR"
    echo "Initialized OpenRouter Free Models Manager"
}

_or_auth_header() {
    echo "Authorization: Bearer ${_OR_API_KEY}"
}

_or_extra_headers() {
    echo "HTTP-Referer: https://github.com/cbwinslow/dotfiles"
    echo "X-Title: CBW OpenRouter Free Models"
}

or_free_models_refresh() {
    if [[ -z "$_OR_API_KEY" ]]; then
        or_free_models_init || return 1
    fi

    echo "Fetching all models from OpenRouter..."

    local response
    response=$(curl -sf \
        -H "$(_or_auth_header)" \
        -H "$(_or_extra_headers)" \
        --max-time 60 \
        "$OR_MODELS_URL")

    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to fetch models" >&2
        return 1
    fi

    _OR_ALL_MODELS_JSON="$response"

    # Extract free models (pricing.prompt == 0 AND pricing.completion == 0)
    local free_models
    free_models=$(echo "$response" | jq '
        .data | map(
            select(.pricing.prompt == "0" or .pricing.prompt == 0) |
            select(.pricing.completion == "0" or .pricing.completion == 0)
        )
    ')

    _OR_FREE_MODELS_JSON="$free_models"

    # Save caches
    echo "$response" > "$OR_ALL_MODELS_CACHE"
    echo "$free_models" > "$OR_FREE_MODELS_CACHE"

    local total free_count
    total=$(echo "$response" | jq '.data | length')
    free_count=$(echo "$free_models" | jq 'length')

    echo "Found $free_count free models out of $total total"
    return 0
}

or_free_models_list() {
    if [[ -z "$_OR_FREE_MODELS_JSON" ]]; then
        if [[ -f "$OR_FREE_MODELS_CACHE" ]]; then
            _OR_FREE_MODELS_JSON=$(cat "$OR_FREE_MODELS_CACHE")
        else
            echo "No models cached. Run or_free_models_refresh first." >&2
            return 1
        fi
    fi

    echo "Free models ($(echo "$_OR_FREE_MODELS_JSON" | jq 'length')):"
    echo "$_OR_FREE_MODELS_JSON" | jq -r '.[] | "  \(.id) - \(.name) (context: \(.context_length))"'
}

or_free_models_test_single() {
    local model_id="$1"
    if [[ -z "$model_id" ]]; then
        echo "Usage: or_free_models_test_single <model_id>" >&2
        return 1
    fi

    local model_name context_length
    if [[ -n "$_OR_FREE_MODELS_JSON" ]]; then
        model_name=$(echo "$_OR_FREE_MODELS_JSON" | jq -r ".[] | select(.id == \"$model_id\") | .name")
        context_length=$(echo "$_OR_FREE_MODELS_JSON" | jq -r ".[] | select(.id == \"$model_id\") | .context_length")
    fi

    if [[ -z "$model_name" || "$model_name" == "null" ]]; then
        model_name="$model_id"
        context_length="unknown"
    fi

    local start_time end_time elapsed_ms http_code response content

    start_time=$(date +%s%N)

    local tmpfile
    tmpfile=$(mktemp)

    http_code=$(curl -sf \
        -H "$(_or_auth_header)" \
        -H "$(_or_extra_headers)" \
        -H "Content-Type: application/json" \
        --max-time "$OR_TEST_TIMEOUT" \
        -w "%{http_code}" \
        -o "$tmpfile" \
        -d "{
            \"model\": \"$model_id\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$OR_TEST_PROMPT\"}],
            \"max_tokens\": 10
        }" \
        "$OR_CHAT_URL" 2>/dev/null) || http_code="000"

    end_time=$(date +%s%N)
    elapsed_ms=$(( (end_time - start_time) / 1000000 ))

    if [[ "$http_code" == "200" ]]; then
        content=$(jq -r '(.choices[0].message.content // "") | if . == "" then (.choices[0].message.reasoning // "") else . end' "$tmpfile" 2>/dev/null)
        rm -f "$tmpfile"
        echo "  ACTIVE: $model_id (${elapsed_ms}ms)"
        echo "    Response: ${content:0:100}"
        return 0
    else
        rm -f "$tmpfile"
        echo "  FAILED: $model_id (HTTP $http_code)"
        return 1
    fi
}

_or_test_worker() {
    local model_id="$1"
    local result_dir="$2"
    local auth_header="$3"
    local extra_headers_1="$4"
    local extra_headers_2="$5"
    local chat_url="$6"
    local test_prompt="$7"
    local test_timeout="$8"
    local free_models_json="$9"

    local model_info
    model_info=$(echo "$free_models_json" | jq -c ".[] | select(.id == \"$model_id\")")
    local model_name context_length
    model_name=$(echo "$model_info" | jq -r '.name // .id')
    context_length=$(echo "$model_info" | jq -r '.context_length // 0')

    local start_time end_time elapsed_ms http_code tmpfile
    start_time=$(date +%s%N)
    tmpfile=$(mktemp)

    http_code=$(curl -sf \
        -H "$auth_header" \
        -H "$extra_headers_1" \
        -H "$extra_headers_2" \
        -H "Content-Type: application/json" \
        --max-time "$test_timeout" \
        -w "%{http_code}" \
        -o "$tmpfile" \
        -d "{
            \"model\": \"$model_id\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$test_prompt\"}],
            \"max_tokens\": 10
        }" \
        "$chat_url" 2>/dev/null) || http_code="000"

    end_time=$(date +%s%N)
    elapsed_ms=$(( (end_time - start_time) / 1000000 ))

    if [[ "$http_code" == "200" ]]; then
        local content
        content=$(jq -r '(.choices[0].message.content // "") | if . == "" then (.choices[0].message.reasoning // "") else . end' "$tmpfile" 2>/dev/null)
        jq -n \
            --arg id "$model_id" \
            --arg name "$model_name" \
            --argjson ctx "$context_length" \
            --argjson time "$elapsed_ms" \
            --arg resp "${content:0:200}" \
            '{model_id: $id, name: $name, context_length: $ctx, tested_at: now, response_time_ms: $time, test_response: $resp, status: "active"}' > "${result_dir}/active_${model_id//\//_}.json"
    else
        jq -n \
            --arg id "$model_id" \
            --arg name "$model_name" \
            --argjson ctx "$context_length" \
            --arg http "$http_code" \
            '{model_id: $id, name: $name, context_length: $ctx, status: "failed", http_code: $http}' > "${result_dir}/failed_${model_id//\//_}.json"
    fi

    rm -f "$tmpfile"
}

or_free_models_test() {
    if [[ -z "$_OR_FREE_MODELS_JSON" ]]; then
        if [[ -f "$OR_FREE_MODELS_CACHE" ]]; then
            _OR_FREE_MODELS_JSON=$(cat "$OR_FREE_MODELS_CACHE")
        else
            or_free_models_refresh || return 1
        fi
    fi

    local model_ids
    model_ids=$(echo "$_OR_FREE_MODELS_JSON" | jq -r '.[].id')
    local total
    total=$(echo "$model_ids" | wc -l | tr -d ' ')

    echo "Testing $total free models (max concurrent: $OR_CONCURRENT)..."

    local result_dir
    result_dir=$(mktemp -d)

    local auth_header="$(_or_auth_header)"
    local extra_1="$(_or_extra_headers | head -1)"
    local extra_2="$(_or_extra_headers | tail -1)"

    local running=0
    local tested=0

    while IFS= read -r model_id; do
        [[ -z "$model_id" ]] && continue

        _or_test_worker "$model_id" "$result_dir" "$auth_header" "$extra_1" "$extra_2" "$OR_CHAT_URL" "$OR_TEST_PROMPT" "$OR_TEST_TIMEOUT" "$_OR_FREE_MODELS_JSON" &

        running=$((running + 1))
        tested=$((tested + 1))

        if (( tested % 5 == 0 )); then
            echo "  Launched $tested/$total..."
        fi

        if (( running >= OR_CONCURRENT )); then
            wait -n 2>/dev/null || wait $(jobs -p | head -1) 2>/dev/null
            running=$((running - 1))
        fi
    done <<< "$model_ids"

    wait

    local active_json="[]"
    local failed_json="[]"

    for f in "$result_dir"/active_*.json; do
        [[ -f "$f" ]] || continue
        local entry
        entry=$(cat "$f")
        active_json=$(echo "$active_json" | jq --argjson e "$entry" '. + [$e]')
    done

    for f in "$result_dir"/failed_*.json; do
        [[ -f "$f" ]] || continue
        local entry
        entry=$(cat "$f")
        failed_json=$(echo "$failed_json" | jq --argjson e "$entry" '. + [$e]')
    done

    echo "$active_json" > "$OR_ACTIVE_MODELS_CACHE"
    echo "$failed_json" > "$OR_FAILED_MODELS_CACHE"

    local active_count failed_count
    active_count=$(echo "$active_json" | jq 'length')
    failed_count=$(echo "$failed_json" | jq 'length')

    rm -rf "$result_dir"

    echo ""
    echo "Results: $active_count active / $failed_count failed / $tested tested"

    if [[ "$active_count" -gt 0 ]]; then
        echo ""
        echo "Active free models:"
        echo "$active_json" | jq -r '.[] | "  \(.model_id) (\(.response_time_ms)ms)"'
    fi

    return 0
}

or_free_models_active() {
    if [[ -f "$OR_ACTIVE_MODELS_CACHE" ]]; then
        local count
        count=$(jq 'length' "$OR_ACTIVE_MODELS_CACHE")
        echo "Active free models ($count):"
        jq -r '.[] | "  \(.model_id) - \(.name) (\(.response_time_ms)ms)"' "$OR_ACTIVE_MODELS_CACHE"
    else
        echo "No active models cached. Run or_free_models_test first." >&2
        return 1
    fi
}

or_free_models_summary() {
    local total=0 free_count=0 active_count=0

    if [[ -f "$OR_ALL_MODELS_CACHE" ]]; then
        total=$(jq '.data | length // 0' "$OR_ALL_MODELS_CACHE" 2>/dev/null || echo 0)
    fi

    if [[ -f "$OR_FREE_MODELS_CACHE" ]]; then
        free_count=$(jq 'length // 0' "$OR_FREE_MODELS_CACHE" 2>/dev/null || echo 0)
    fi

    if [[ -f "$OR_ACTIVE_MODELS_CACHE" ]]; then
        active_count=$(jq 'length // 0' "$OR_ACTIVE_MODELS_CACHE" 2>/dev/null || echo 0)
    fi

    echo "{"
    echo "  \"total_models\": $total,"
    echo "  \"free_models\": $free_count,"
    echo "  \"active_free_models\": $active_count"
    echo "}"
}

# CLI entry point when run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        refresh)
            or_free_models_init "${2:-}" || exit 1
            or_free_models_refresh
            ;;
        list)
            or_free_models_init "${2:-}" || exit 1
            or_free_models_list
            ;;
        test)
            or_free_models_init "${2:-}" || exit 1
            or_free_models_test
            ;;
        test-single)
            or_free_models_init "${2:-}" || exit 1
            or_free_models_test_single "${3:-}"
            ;;
        active)
            or_free_models_active
            ;;
        summary)
            or_free_models_summary
            ;;
        *)
            echo "Usage: $0 {refresh|list|test|test-single <model_id>|active|summary} [api_key]"
            exit 1
            ;;
    esac
fi
