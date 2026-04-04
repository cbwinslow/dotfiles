#!/usr/bin/env bash
# Worktree Manager for AI Agent Dotfiles
# Manages git worktrees for different branches/machines

set -euo pipefail

CHEZMOI_REPO="${HOME}/.local/share/chezmoi"
WORKTREE_BASE="${HOME}/.local/share/chezmoi-worktrees"

usage() {
    cat <<EOF
Usage: $0 <command> [options]

Commands:
    list                    List all worktrees
    create <branch> <name>  Create a new worktree for a branch
    checkout <name>         Checkout (cd) to a worktree
    remove <name>           Remove a worktree
    sync <name>             Sync worktree with remote (pull & apply)
    
Examples:
    $0 create develop my-devel
    $0 list
    $0 sync my-devel
    $0 checkout my-devel

Environment Variables:
    CHEZMOI_REPO      Default: $HOME/.local/share/chezmoi
    WORKTREE_BASE     Default: $HOME/.local/share/chezmoi-worktrees

EOF
}

list_worktrees() {
    echo "=== Available Worktrees ==="
    if [[ ! -d "$WORKTREE_BASE" ]]; then
        echo "No worktrees created yet."
        return 0
    fi
    
    for wt in "$WORKTREE_BASE"/*; do
        [[ -d "$wt" ]] || continue
        name=$(basename "$wt")
        branch=$(git --work-tree="$wt" --git-dir="$CHEZMOI_REPO" branch --show-current 2>/dev/null || echo "unknown")
        echo "  $name (branch: $branch)"
    done
}

create_worktree() {
    local branch_name="$1"
    local worktree_name="$2"
    
    if [[ -z "$branch_name" || -z "$worktree_name" ]]; then
        echo "Error: branch and name required"
        usage
        exit 1
    fi
    
    # Ensure branch exists locally or remotely
    if ! git --git-dir="$CHEZMOI_REPO" branch --list | grep -q "^[* ]*$branch_name$"; then
        if git --git-dir="$CHEZMOI_REPO" ls-remote --heads origin "$branch_name" | grep -q "$branch_name"; then
            git --git-dir="$CHEZMOI_REPO" branch "$branch_name" "origin/$branch_name"
        else
            echo "Error: branch '$branch_name' does not exist locally or remotely"
            exit 1
        fi
    fi
    
    mkdir -p "$WORKTREE_BASE"
    local worktree_path="$WORKTREE_BASE/$worktree_name"
    
    if [[ -d "$worktree_path" ]]; then
        echo "Error: worktree '$worktree_name' already exists at $worktree_path"
        exit 1
    fi
    
    echo "Creating worktree '$worktree_name' from branch '$branch_name'..."
    git --git-dir="$CHEZMOI_REPO" worktree add -b "$branch_name" "$worktree_path" "$branch_name"
    
    # Initialize chezmoi in the new worktree
    (
        cd "$worktree_path"
        chezmoi init --source "$CHEZMOI_REPO"
    )
    
    echo "Worktree created at: $worktree_path"
    echo "To apply: (cd $worktree_path && chezmoi apply)"
}

checkout_worktree() {
    local name="$1"
    local worktree_path="$WORKTREE_BASE/$name"
    
    if [[ ! -d "$worktree_path" ]]; then
        echo "Error: worktree '$name' not found"
        list_worktrees
        exit 1
    fi
    
    echo "cd $worktree_path"
    # shellcheck disable=SC2164
    cd "$worktree_path" || exit 1
    echo "Current branch: $(git branch --show-current)"
    echo "Run: chezmoi apply"
}

remove_worktree() {
    local name="$1"
    local worktree_path="$WORKTREE_BASE/$name"
    
    if [[ ! -d "$worktree_path" ]]; then
        echo "Error: worktree '$name' not found"
        exit 1
    fi
    
    git --git-dir="$CHEZMOI_REPO" worktree remove "$worktree_path"
    echo "Worktree '$name' removed"
}

sync_worktree() {
    local name="$1"
    local worktree_path="$WORKTREE_BASE/$name"
    
    if [[ ! -d "$worktree_path" ]]; then
        echo "Error: worktree '$name' not found"
        exit 1
    fi
    
    (
        cd "$worktree_path"
        echo "Syncing worktree '$name'..."
        git fetch origin
        git merge origin/$(git branch --show-current) --ff-only || {
            echo "Warning: Fast-forward merge not possible. Manual intervention needed."
            exit 1
        }
        echo "Applying chezmoi configuration..."
        chezmoi apply --verbose
        echo "Sync complete."
    )
}

# Main
case "${1:-}" in
    list)
        list_worktrees
        ;;
    create)
        create_worktree "$2" "$3"
        ;;
    checkout)
        checkout_worktree "$2"
        ;;
    remove)
        remove_worktree "$2"
        ;;
    sync)
        sync_worktree "$2"
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Error: unknown command '$1'"
        usage
        exit 1
        ;;
esac
