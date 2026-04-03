#!/bin/bash
# tailscale_sync.sh - Sync configurations across Tailscale network
# This script synchronizes AI agent configurations across multiple machines

set -e

# Configuration
SHARED_PATH="/mnt/tailscale-shared/ai-configs"
LOCAL_PATH="$HOME/dotfiles/ai"
SYNC_INTERVAL="5m"
LOG_FILE="$HOME/dotfiles/ai/logs/tailscale_sync.log"
PID_FILE="/tmp/tailscale_sync.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if Tailscale is running
check_tailscale() {
    if ! command -v tailscale >/dev/null 2>&1; then
        error "Tailscale is not installed or not in PATH"
        return 1
    fi
    
    if ! tailscale status >/dev/null 2>&1; then
        error "Tailscale is not running or not connected"
        return 1
    fi
    
    return 0
}

# Function to check if shared path is mounted
check_shared_path() {
    if [ ! -d "$SHARED_PATH" ]; then
        warning "Shared path not found: $SHARED_PATH"
        return 1
    fi
    
    # Check if it's actually mounted (not just a local directory)
    if ! mountpoint -q "$SHARED_PATH" 2>/dev/null; then
        warning "Shared path is not mounted: $SHARED_PATH"
        return 1
    fi
    
    return 0
}

# Function to create necessary directories
setup_directories() {
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$SHARED_PATH"
    mkdir -p "$LOCAL_PATH"
}

# Function to sync from shared to local
sync_from_shared() {
    if [ ! -d "$SHARED_PATH" ]; then
        return 0
    fi
    
    log "Syncing from shared to local..."
    
    # Use rsync for efficient syncing
    if rsync -av --delete "$SHARED_PATH/" "$LOCAL_PATH/" 2>/dev/null; then
        success "✓ Synced from shared to local"
        return 0
    else
        error "Failed to sync from shared to local"
        return 1
    fi
}

# Function to sync from local to shared
sync_to_shared() {
    if [ ! -d "$LOCAL_PATH" ]; then
        return 0
    fi
    
    log "Syncing from local to shared..."
    
    # Use rsync for efficient syncing
    if rsync -av --delete "$LOCAL_PATH/" "$SHARED_PATH/" 2>/dev/null; then
        success "✓ Synced from local to shared"
        return 0
    else
        error "Failed to sync from local to shared"
        return 1
    fi
}

# Function to detect changes
detect_changes() {
    local local_checksum="$LOCAL_PATH/.checksum"
    local shared_checksum="$SHARED_PATH/.checksum"
    
    # Generate checksums
    find "$LOCAL_PATH" -type f -exec md5sum {} \; 2>/dev/null | sort > "$local_checksum.tmp" || true
    find "$SHARED_PATH" -type f -exec md5sum {} \; 2>/dev/null | sort > "$shared_checksum.tmp" || true
    
    # Compare checksums
    if ! diff -q "$local_checksum.tmp" "$shared_checksum.tmp" >/dev/null 2>&1; then
        # Changes detected
        mv "$local_checksum.tmp" "$local_checksum"
        mv "$shared_checksum.tmp" "$shared_checksum"
        return 0
    else
        # No changes
        rm -f "$local_checksum.tmp" "$shared_checksum.tmp"
        return 1
    fi
}

# Function to run sync cycle
run_sync_cycle() {
    log "Starting sync cycle..."
    
    # Check Tailscale status
    if ! check_tailscale; then
        warning "Tailscale is not available, skipping sync"
        return 1
    fi
    
    # Check shared path
    if ! check_shared_path; then
        warning "Shared path is not available, skipping sync"
        return 1
    fi
    
    # Detect changes
    if detect_changes; then
        log "Changes detected, performing sync..."
        
        # Sync in both directions
        local sync_success=true
        
        if ! sync_from_shared; then
            sync_success=false
        fi
        
        if ! sync_to_shared; then
            sync_success=false
        fi
        
        if $sync_success; then
            success "✓ Sync completed successfully"
            return 0
        else
            error "Sync failed"
            return 1
        fi
    else
        log "No changes detected, skipping sync"
        return 0
    fi
}

# Function to start sync daemon
start_daemon() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        warning "Sync daemon is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    log "Starting Tailscale configuration sync daemon..."
    
    # Start daemon in background
    (
        echo $$ > "$PID_FILE"
        log "Sync daemon started with PID: $$"
        
        while true; do
            run_sync_cycle
            sleep "$(echo $SYNC_INTERVAL | sed 's/m/*60/g' | sed 's/s//g' | bc 2>/dev/null || echo 300)"
        done
    ) &
    
    # Wait a moment to ensure daemon started
    sleep 1
    
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        success "✓ Sync daemon started successfully"
        echo "PID: $(cat "$PID_FILE")"
        echo "Log file: $LOG_FILE"
        return 0
    else
        error "Failed to start sync daemon"
        return 1
    fi
}

# Function to stop sync daemon
stop_daemon() {
    if [ ! -f "$PID_FILE" ]; then
        warning "Sync daemon is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        log "Stopping sync daemon (PID: $pid)..."
        kill "$pid"
        
        # Wait for process to stop
        sleep 2
        
        if kill -0 "$pid" 2>/dev/null; then
            warning "Process did not stop gracefully, forcing termination..."
            kill -9 "$pid"
        fi
        
        rm -f "$PID_FILE"
        success "✓ Sync daemon stopped"
        return 0
    else
        warning "Sync daemon is not running"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to check daemon status
check_status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        local pid=$(cat "$PID_FILE")
        success "Sync daemon is running (PID: $pid)"
        
        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            echo
            echo "Recent log entries:"
            tail -10 "$LOG_FILE"
        fi
        return 0
    else
        warning "Sync daemon is not running"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "Tailscale Configuration Sync Script"
    echo "==================================="
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  start     Start the sync daemon"
    echo "  stop      Stop the sync daemon"
    echo "  restart   Restart the sync daemon"
    echo "  status    Show daemon status"
    echo "  sync      Perform a single sync operation"
    echo "  test      Test Tailscale and shared path connectivity"
    echo "  help      Show this help message"
    echo
    echo "Configuration:"
    echo "  Shared Path: $SHARED_PATH"
    echo "  Local Path:  $LOCAL_PATH"
    echo "  Sync Interval: $SYNC_INTERVAL"
    echo "  Log File:    $LOG_FILE"
    echo
    echo "Environment Variables:"
    echo "  TAILSCALE_SHARED_PATH    Override shared path"
    echo "  TAILSCALE_LOCAL_PATH     Override local path"
    echo "  TAILSCALE_SYNC_INTERVAL  Override sync interval"
    echo "  TAILSCALE_LOG_FILE       Override log file"
}

# Function to test connectivity
test_connectivity() {
    log "Testing Tailscale connectivity..."
    
    if check_tailscale; then
        success "✓ Tailscale is running and connected"
    else
        error "✗ Tailscale is not available"
        return 1
    fi
    
    log "Testing shared path..."
    
    if check_shared_path; then
        success "✓ Shared path is mounted and accessible"
    else
        error "✗ Shared path is not available"
        return 1
    fi
    
    log "Testing sync operation..."
    
    if run_sync_cycle; then
        success "✓ Sync operation completed successfully"
    else
        error "✗ Sync operation failed"
        return 1
    fi
    
    success "✓ All connectivity tests passed"
}

# Function to perform single sync
single_sync() {
    log "Performing single sync operation..."
    
    if run_sync_cycle; then
        success "✓ Single sync completed successfully"
        return 0
    else
        error "✗ Single sync failed"
        return 1
    fi
}

# Main execution
main() {
    # Override defaults with environment variables if set
    [ ! -z "$TAILSCALE_SHARED_PATH" ] && SHARED_PATH="$TAILSCALE_SHARED_PATH"
    [ ! -z "$TAILSCALE_LOCAL_PATH" ] && LOCAL_PATH="$TAILSCALE_LOCAL_PATH"
    [ ! -z "$TAILSCALE_SYNC_INTERVAL" ] && SYNC_INTERVAL="$TAILSCALE_SYNC_INTERVAL"
    [ ! -z "$TAILSCALE_LOG_FILE" ] && LOG_FILE="$TAILSCALE_LOG_FILE"
    
    # Setup directories
    setup_directories
    
    # Parse command line arguments
    case "${1:-help}" in
        "start")
            start_daemon
            ;;
        "stop")
            stop_daemon
            ;;
        "restart")
            stop_daemon
            sleep 2
            start_daemon
            ;;
        "status")
            check_status
            ;;
        "sync")
            single_sync
            ;;
        "test")
            test_connectivity
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"