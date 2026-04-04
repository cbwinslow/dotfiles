#!/bin/bash
# CBW Help - Shell integration for the RAG knowledge base
# Add this to your .zshrc or .bashrc

cbw-help() {
    local query="$1"
    if [ -z "$query" ]; then
        echo "Usage: cbw-help <query>"
        echo "Examples:"
        echo "  cbw-help 'psql backup'"
        echo "  cbw-help 'docker compose'"
        echo "  cbw-help --interactive"
        return 1
    fi
    
    source /home/cbwinslow/workspace/epstein/.venv/bin/activate 2>/dev/null
    python3 /home/cbwinslow/dotfiles/ai/scripts/cbw_kb.py "$query"
}

cbw-pattern() {
    python3 /home/cbwinslow/dotfiles/ai/scripts/script_pattern_analyzer.py --report
}

cbw-validate() {
    if [ -f "$1" ]; then
        python3 /home/cbwinslow/dotfiles/ai/scripts/config_validator.py --validate "$1"
    else
        python3 /home/cbwinslow/dotfiles/ai/scripts/config_validator.py --scan-all
    fi
}

cbw-doc() {
    if [ -f "$1" ]; then
        python3 /home/cbwinslow/dotfiles/ai/scripts/cbw_doc.py --doc "$1"
    else
        echo "Usage: cbw-doc <script.sh>"
    fi
}

cbw-recommend() {
    local task="$1"
    if [ -z "$task" ]; then
        echo "Usage: cbw-recommend <task>"
        echo "Examples:"
        echo "  cbw-recommend 'database backup'"
        echo "  cbw-recommend 'docker deployment'"
        return 1
    fi
    
    python3 /home/cbwinslow/dotfiles/ai/scripts/recommender.py --task "$task"
}

cbw-index() {
    if [ -z "$1" ]; then
        echo "Usage: cbw-index <directory>"
        echo "  cbw-index ~/dotfiles"
        echo "  cbw-index ~/workspace/myproject"
        return 1
    fi
    
    source ~/.bash_secrets 2>/dev/null
    source /home/cbwinslow/workspace/epstein/.venv/bin/activate
    python3 /home/cbwinslow/projects/ai/rag_system/cbw_indexer.py "$1" --db "$CBW_RAG_DATABASE" --use-ollama --quiet
}

# Organization tools
cbw-reuse() {
    python3 ~/dotfiles/ai/scripts/cbw_reuse.py "$@"
}

cbw-tasks() {
    python3 ~/dotfiles/ai/scripts/cbw_tasks.py "$@"
}

cbw-deps() {
    python3 ~/dotfiles/ai/scripts/cbw_deps.py "$@"
}

cbw-agents-md() {
    if [ -z "$1" ]; then
        python3 ~/dotfiles/ai/scripts/generate_agents_md.py . --recursive --depth 3
    else
        python3 ~/dotfiles/ai/scripts/generate_agents_md.py "$1" --recursive --depth 3
    fi
}

# Debug and analysis tools
cbw-debug() {
    python3 ~/dotfiles/ai/scripts/cbw_debug.py "$@"
}

cbw-analyze() {
    python3 ~/dotfiles/ai/scripts/cbw_analyze.py "$@"
}

cbw-visualize() {
    python3 ~/dotfiles/ai/scripts/cbw_visualize.py "$@"
}

# Documentation & Research
cbw-doc-fetch() {
    python3 ~/dotfiles/ai/scripts/cbw_doc_fetch.py "$@"
}

alias doc-fetch='cbw-doc-fetch'
alias fetch-docs='cbw-doc-fetch'

# Skill discovery
cbw-skills() {
    python3 ~/dotfiles/ai/scripts/cbw_skills.py "$@"
}

alias skills='cbw-skills'
alias skill-list='cbw-skills --list'
alias skill-info='cbw-skills --info'

# Letta automation
cbw-letta() {
    python3 ~/dotfiles/ai/scripts/cbw_letta.py "$@"
}

alias letta='cbw-letta'
alias kbi='cbw-help --interactive'
alias validate-agent='cbw-validate'
alias doc-script='cbw-doc'
alias debug='cbw-debug'
alias analyze='cbw-analyze'
alias visualize='cbw-visualize'
alias reuse='cbw-reuse'
alias tasks='cbw-tasks'
alias deps='cbw-deps'
alias agents-md='cbw-agents-md'
