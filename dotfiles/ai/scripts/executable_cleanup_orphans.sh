#!/bin/bash
# Cleanup script for orphaned AI dotfiles
# Removes duplicate skills, old registry files, and agent-specific duplicates

set -e

DOTFILES_AI="${HOME}/dotfiles/ai"
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}AI Dotfiles Cleanup Script${NC}"
echo "============================"
echo ""

# Function to confirm deletion
confirm() {
    read -p "Delete $1? (y/N): " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# ============================================
# 1. Remove orphaned files in skills/ directory
# ============================================
echo -e "${YELLOW}Phase 1: Cleaning up orphaned skill files...${NC}"

ORPHANED_FILES=(
    "${DOTFILES_AI}/skills/.skillsrc"
    "${DOTFILES_AI}/skills/skills"
    "${DOTFILES_AI}/skills/run_all_skills.sh"
    "${DOTFILES_AI}/skills/setup_agent_skills_cli.sh"
    "${DOTFILES_AI}/skills/setup_unified_skills.sh"
    "${DOTFILES_AI}/skills/UNIFIED_SKILLS.md"
    "${DOTFILES_AI}/skills/SKILL_INDEX.md"
    "${DOTFILES_AI}/skills/skill_symlinker.py"
    "${DOTFILES_AI}/skills/skill_registry.json"
)

for file in "${ORPHANED_FILES[@]}"; do
    if [ -f "$file" ]; then
        if confirm "$file"; then
            rm -f "$file"
            echo -e "${GREEN}  Removed: $file${NC}"
        fi
    fi
done

# ============================================
# 2. Remove empty/legacy .system directory
# ============================================
echo ""
echo -e "${YELLOW}Phase 2: Cleaning up .system directory...${NC}"

if [ -d "${DOTFILES_AI}/skills/.system" ]; then
    # Check if it only contains empty markers
    if [ -f "${DOTFILES_AI}/skills/.system/.codex-system-skills.marker" ]; then
        if confirm "${DOTFILES_AI}/skills/.system (contains only legacy marker)"; then
            rm -rf "${DOTFILES_AI}/skills/.system"
            echo -e "${GREEN}  Removed: .system directory${NC}"
        fi
    fi
fi

# ============================================
# 3. Clean up duplicate letta_integration in skills/
# ============================================
echo ""
echo -e "${YELLOW}Phase 3: Consolidating letta_integration...${NC}"

# The canonical location is packages/letta_integration/
# skills/letta_integration/ should only have SKILL.md pointing to packages/

if [ -d "${DOTFILES_AI}/skills/letta_integration" ]; then
    echo -e "${YELLOW}  Found skills/letta_integration/${NC}"
    echo -e "  Canonical location: packages/letta_integration/"
    
    if confirm "Remove skills/letta_integration/letta_integration (nested duplicate)"; then
        rm -rf "${DOTFILES_AI}/skills/letta_integration/letta_integration"
        echo -e "${GREEN}  Removed nested duplicate${NC}"
    fi
    
    if confirm "Remove skills/letta_integration/*.py and *.sh (use packages/ instead)"; then
        rm -f "${DOTFILES_AI}/skills/letta_integration/"*.py
        rm -f "${DOTFILES_AI}/skills/letta_integration/"*.sh
        echo -e "${GREEN}  Removed duplicate scripts${NC}"
    fi
fi

# ============================================
# 4. Remove duplicate model_picker skills
# ============================================
echo ""
echo -e "${YELLOW}Phase 4: Consolidating model_picker skills...${NC}"

# Keep only one: skills/letta_model_picker/ (most specific)
# Remove: skills/model_picker/

if [ -d "${DOTFILES_AI}/skills/model_picker" ] && [ -d "${DOTFILES_AI}/skills/letta_model_picker" ]; then
    if confirm "Remove skills/model_picker/ (duplicate of letta_model_picker)"; then
        rm -rf "${DOTFILES_AI}/skills/model_picker"
        echo -e "${GREEN}  Removed duplicate model_picker${NC}"
    fi
fi

# ============================================
# 5. Clean up packages/letta_integration agent directories
# ============================================
echo ""
echo -e "${YELLOW}Phase 5: Cleaning up duplicate agent directories in packages...${NC}"

PACKAGES_LETTA="${DOTFILES_AI}/packages/letta_integration"

if [ -d "$PACKAGES_LETTA" ]; then
    # Count agent directories (starting with .)
    AGENT_DIRS=$(find "$PACKAGES_LETTA" -maxdepth 1 -type d -name ".*" | wc -l)
    
    if [ "$AGENT_DIRS" -gt 0 ]; then
        echo -e "${YELLOW}  Found ${AGENT_DIRS} hidden agent directories${NC}"
        echo "  These contain duplicate skills for each agent"
        
        if confirm "Remove ALL .*/agent directories from packages/letta_integration/"; then
            find "$PACKAGES_LETTA" -maxdepth 1 -type d -name ".*" -exec rm -rf {} + 2>/dev/null || true
            echo -e "${GREEN}  Removed all agent duplicate directories${NC}"
        fi
    fi
fi

# ============================================
# 6. Clean up duplicate skills in shared/
# ============================================
echo ""
echo -e "${YELLOW}Phase 6: Analyzing shared/skills for duplicates...${NC}"

# Check for duplicates between skills/ and shared/skills/
if [ -d "${DOTFILES_AI}/shared/skills" ]; then
    for skill_dir in "${DOTFILES_AI}/shared/skills"/*; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            if [ -d "${DOTFILES_AI}/skills/${skill_name}" ]; then
                echo -e "${YELLOW}  Duplicate found: ${skill_name}${NC}"
                echo "    - shared/skills/${skill_name}/"
                echo "    - skills/${skill_name}/"
            fi
        fi
    done
fi

# ============================================
# 7. Fix conversation_logger vs conversation_logging naming
# ============================================
echo ""
echo -e "${YELLOW}Phase 7: Consolidating conversation logging skills...${NC}"

if [ -d "${DOTFILES_AI}/skills/conversation_logger" ] && [ -d "${DOTFILES_AI}/skills/conversation_logging" ]; then
    echo "Found both conversation_logger and conversation_logging"
    if confirm "Merge conversation_logging into conversation_logger"; then
        # Move unique files from conversation_logging to conversation_logger
        if [ -f "${DOTFILES_AI}/skills/conversation_logging/SKILL.md" ]; then
            mv "${DOTFILES_AI}/skills/conversation_logging/SKILL.md" \
               "${DOTFILES_AI}/skills/conversation_logger/SKILL_v2.md"
        fi
        rm -rf "${DOTFILES_AI}/skills/conversation_logging"
        echo -e "${GREEN}  Merged and removed conversation_logging${NC}"
    fi
fi

# ============================================
# 8. Clean up old registry files
# ============================================
echo ""
echo -e "${YELLOW}Phase 8: Cleaning up old registry files...${NC}"

OLD_REGISTRIES=(
    "${DOTFILES_AI}/skills/registry.json"
    "${DOTFILES_AI}/shared/skills/registry.yaml"
)

for reg in "${OLD_REGISTRIES[@]}"; do
    if [ -f "$reg" ]; then
        echo -e "${YELLOW}  Found: $reg${NC}"
        echo "    This may be superseded by the new config.yaml system"
    fi
done

# ============================================
# 9. Check for workflows in wrong location
# ============================================
echo ""
echo -e "${YELLOW}Phase 9: Checking workflow locations...${NC}"

if [ -d "${DOTFILES_AI}/skills/workflows" ]; then
    WORKFLOW_COUNT=$(find "${DOTFILES_AI}/skills/workflows" -type f -name "*.md" | wc -l)
    if [ "$WORKFLOW_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}  Found ${WORKFLOW_COUNT} workflows in skills/workflows/${NC}"
        echo "  Should be in top-level workflows/"
        
        if confirm "Move workflows from skills/workflows/ to workflows/"; then
            mv "${DOTFILES_AI}/skills/workflows/"*.md "${DOTFILES_AI}/workflows/" 2>/dev/null || true
            rmdir "${DOTFILES_AI}/skills/workflows" 2>/dev/null || true
            echo -e "${GREEN}  Moved workflows${NC}"
        fi
    fi
fi

# ============================================
# Summary
# ============================================
echo ""
echo -e "${GREEN}============================${NC}"
echo -e "${GREEN}Cleanup Summary${NC}"
echo -e "${GREEN}============================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review remaining duplicates in shared/skills/ vs skills/"
echo "  2. Update registry.yaml to reflect current skill locations"
echo "  3. Run setup.sh to create symlinks to ~/.config/ai"
echo "  4. Verify agents still load correctly"
echo ""
echo "To see what remains:"
echo "  find ${DOTFILES_AI}/skills -type d | sort"
echo ""
