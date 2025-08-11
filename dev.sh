#!/bin/bash

# Unraid MCP Server Development Script
# Safely manages server processes during development with accurate process detection

set -euo pipefail

# Configuration
DEFAULT_PORT=6970
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/dev.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for colored output
log() {
    echo -e "${2:-$NC}[$(date +'%H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Get port from environment or use default
get_port() {
    local port="${UNRAID_MCP_PORT:-$DEFAULT_PORT}"
    echo "$port"
}

# Find processes using multiple detection methods
find_server_processes() {
    local port=$(get_port)
    local pids=()
    
    # Method 1: Command line pattern matching
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            local pid=$(echo "$line" | awk '{print $2}')
            local cmd=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
            pids+=("$pid")
        fi
    done < <(ps aux | grep -E 'python.*unraid.*mcp|python.*main\.py|uv run.*main\.py|uv run -m unraid_mcp' | grep -v grep | grep -v "$0")
    
    # Method 2: Port binding verification
    if command -v lsof >/dev/null 2>&1; then
        while IFS= read -r line; do
            if [[ -n "$line" ]]; then
                local pid=$(echo "$line" | awk '{print $2}')
                # Add to pids if not already present
                if [[ ! " ${pids[@]} " =~ " $pid " ]]; then
                    pids+=("$pid")
                fi
            fi
        done < <(lsof -i ":$port" 2>/dev/null | grep LISTEN || true)
    fi
    
    # Method 3: Working directory verification
    local verified_pids=()
    for pid in "${pids[@]}"; do
        # Skip if not a valid PID
        if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
            continue
        fi
        
        if [[ -d "/proc/$pid" ]]; then
            local pwd_info=""
            if command -v pwdx >/dev/null 2>&1; then
                pwd_info=$(pwdx "$pid" 2>/dev/null | cut -d' ' -f2- || echo "unknown")
            else
                pwd_info=$(readlink -f "/proc/$pid/cwd" 2>/dev/null || echo "unknown")
            fi
            
            # Verify it's running from our project directory or a parent directory
            if [[ "$pwd_info" == "$PROJECT_DIR"* ]] || [[ "$pwd_info" == *"unraid-mcp"* ]]; then
                verified_pids+=("$pid")
            fi
        fi
    done
    
    # Output final list
    printf '%s\n' "${verified_pids[@]}" | grep -E '^[0-9]+$' || true
}

# Terminate a process gracefully, then forcefully if needed
terminate_process() {
    local pid=$1
    local name=${2:-"process"}
    
    if ! kill -0 "$pid" 2>/dev/null; then
        log "Process $pid ($name) already terminated" "$YELLOW"
        return 0
    fi
    
    log "Terminating $name (PID: $pid)..." "$YELLOW"
    
    # Step 1: Graceful shutdown (SIGTERM)
    log "  → Sending SIGTERM to PID $pid" "$BLUE"
    kill -TERM "$pid" 2>/dev/null || {
        log "    Failed to send SIGTERM (process may have died)" "$YELLOW"
        return 0
    }
    
    # Step 2: Wait for graceful shutdown (5 seconds)
    local count=0
    while [[ $count -lt 5 ]]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            log "  ✓ Process $pid terminated gracefully" "$GREEN"
            return 0
        fi
        sleep 1
        ((count++))
        log "    Waiting for graceful shutdown... (${count}/5)" "$BLUE"
    done
    
    # Step 3: Force kill (SIGKILL)
    log "  → Graceful shutdown timeout, sending SIGKILL to PID $pid" "$RED"
    kill -KILL "$pid" 2>/dev/null || {
        log "    Failed to send SIGKILL (process may have died)" "$YELLOW"
        return 0
    }
    
    # Step 4: Final verification
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
        log "  ✗ Failed to terminate process $pid" "$RED"
        return 1
    else
        log "  ✓ Process $pid terminated forcefully" "$GREEN"
        return 0
    fi
}

# Stop all server processes
stop_servers() {
    log "🛑 Stopping existing server processes..." "$RED"
    
    local pids=($(find_server_processes))
    
    if [[ ${#pids[@]} -eq 0 ]]; then
        log "No processes to stop" "$GREEN"
        return 0
    fi
    
    local failed=0
    for pid in "${pids[@]}"; do
        if ! terminate_process "$pid" "Unraid MCP Server"; then
            ((failed++))
        fi
    done
    
    # Wait for ports to be released
    local port=$(get_port)
    log "Waiting for port $port to be released..." "$BLUE"
    local port_wait=0
    while [[ $port_wait -lt 3 ]]; do
        if ! lsof -i ":$port" >/dev/null 2>&1; then
            log "✓ Port $port released" "$GREEN"
            break
        fi
        sleep 1
        ((port_wait++))
    done
    
    if [[ $failed -gt 0 ]]; then
        log "⚠️  Failed to stop $failed process(es)" "$RED"
        return 1
    else
        log "✅ All processes stopped successfully" "$GREEN"
        return 0
    fi
}

# Start the new modular server
start_modular_server() {
    log "🚀 Starting modular server..." "$GREEN"
    
    cd "$PROJECT_DIR"
    
    # Check if main.py exists in unraid_mcp/
    if [[ ! -f "unraid_mcp/main.py" ]]; then
        log "❌ unraid_mcp/main.py not found. Make sure modular server is implemented." "$RED"
        return 1
    fi
    
    # Start server in background using module syntax
    log "  → Executing: uv run -m unraid_mcp.main" "$BLUE"
    nohup uv run -m unraid_mcp.main >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Give it a moment to start
    sleep 2
    
    # Check if it's still running
    if kill -0 "$pid" 2>/dev/null; then
        local port=$(get_port)
        log "✅ Modular server started successfully (PID: $pid, Port: $port)" "$GREEN"
        log "📋 Process info: $(ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null || echo 'Process info unavailable')" "$BLUE"
        
        # Auto-tail logs after successful start
        echo ""
        log "📄 Following server logs in real-time..." "$GREEN"
        log "Press Ctrl+C to stop following logs (server will continue running)" "$YELLOW"
        echo ""
        echo -e "${GREEN}=== Following Server Logs (Press Ctrl+C to exit) ===${NC}"
        tail -f "$LOG_FILE"
        
        return 0
    else
        log "❌ Modular server failed to start" "$RED"
        log "📄 Check $LOG_FILE for error details" "$YELLOW"
        return 1
    fi
}

# Start the original server
start_original_server() {
    log "🚀 Starting original server..." "$GREEN"
    
    cd "$PROJECT_DIR"
    
    # Check if original server exists
    if [[ ! -f "unraid_mcp_server.py" ]]; then
        log "❌ unraid_mcp_server.py not found" "$RED"
        return 1
    fi
    
    # Start server in background
    log "  → Executing: uv run unraid_mcp_server.py" "$BLUE"
    nohup uv run unraid_mcp_server.py >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Give it a moment to start
    sleep 2
    
    # Check if it's still running
    if kill -0 "$pid" 2>/dev/null; then
        local port=$(get_port)
        log "✅ Original server started successfully (PID: $pid, Port: $port)" "$GREEN"
        log "📋 Process info: $(ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null || echo 'Process info unavailable')" "$BLUE"
        
        # Auto-tail logs after successful start
        echo ""
        log "📄 Following server logs in real-time..." "$GREEN"
        log "Press Ctrl+C to stop following logs (server will continue running)" "$YELLOW"
        echo ""
        echo -e "${GREEN}=== Following Server Logs (Press Ctrl+C to exit) ===${NC}"
        tail -f "$LOG_FILE"
        
        return 0
    else
        log "❌ Original server failed to start" "$RED"
        log "📄 Check $LOG_FILE for error details" "$YELLOW"
        return 1
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Development script for Unraid MCP Server"
    echo ""
    echo "OPTIONS:"
    echo "  (no args)     Stop existing servers, start modular server, and tail logs"
    echo "  --old         Stop existing servers, start original server, and tail logs"
    echo "  --kill        Stop existing servers only (don't start new one)"
    echo "  --status      Show status of running servers"
    echo "  --logs [N]    Show last N lines of server logs (default: 50)"
    echo "  --tail        Follow server logs in real-time (without restarting server)"
    echo "  --help, -h    Show this help message"
    echo ""
    echo "ENVIRONMENT VARIABLES:"
    echo "  UNRAID_MCP_PORT    Port for server (default: $DEFAULT_PORT)"
    echo ""
    echo "EXAMPLES:"
    echo "  ./dev.sh              # Restart with modular server"
    echo "  ./dev.sh --old        # Restart with original server"
    echo "  ./dev.sh --kill       # Stop all servers"
    echo "  ./dev.sh --status     # Check server status"
    echo "  ./dev.sh --logs       # Show last 50 lines of logs"
    echo "  ./dev.sh --logs 100   # Show last 100 lines of logs"
    echo "  ./dev.sh --tail       # Follow logs in real-time"
}

# Show server status
show_status() {
    local port=$(get_port)
    log "🔍 Server Status Check" "$BLUE"
    log "Project Directory: $PROJECT_DIR" "$BLUE"
    log "Expected Port: $port" "$BLUE"
    echo ""
    
    local pids=($(find_server_processes))
    
    if [[ ${#pids[@]} -eq 0 ]]; then
        log "Status: No servers running" "$YELLOW"
    else
        log "Status: ${#pids[@]} server(s) running" "$GREEN"
        for pid in "${pids[@]}"; do
            local cmd=$(ps -p "$pid" -o cmd --no-headers 2>/dev/null || echo "Command unavailable")
            log "  PID $pid: $cmd" "$GREEN"
        done
    fi
    
    # Check port binding
    if command -v lsof >/dev/null 2>&1; then
        local port_info=$(lsof -i ":$port" 2>/dev/null | grep LISTEN || echo "")
        if [[ -n "$port_info" ]]; then
            log "Port $port: BOUND" "$GREEN"
            echo "$port_info" | while IFS= read -r line; do
                log "  $line" "$BLUE"
            done
        else
            log "Port $port: FREE" "$YELLOW"
        fi
    fi
}

# Tail the server logs
tail_logs() {
    local lines="${1:-50}"
    
    log "📄 Tailing last $lines lines from server logs..." "$BLUE"
    
    if [[ ! -f "$LOG_FILE" ]]; then
        log "❌ Log file not found: $LOG_FILE" "$RED"
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}=== Server Logs (last $lines lines) ===${NC}"
    tail -n "$lines" "$LOG_FILE"
    echo -e "${YELLOW}=== End of Logs ===${NC}"
    echo ""
}

# Follow server logs in real-time
follow_logs() {
    log "📄 Following server logs in real-time..." "$GREEN"
    log "Press Ctrl+C to stop following" "$YELLOW"
    
    if [[ ! -f "$LOG_FILE" ]]; then
        log "❌ Log file not found: $LOG_FILE" "$RED"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}=== Following Server Logs (Press Ctrl+C to exit) ===${NC}"
    tail -f "$LOG_FILE"
}

# Main script logic
main() {
    # Initialize log file
    echo "=== Dev Script Started at $(date) ===" >> "$LOG_FILE"
    
    case "${1:-}" in
        --help|-h)
            show_usage
            ;;
        --status)
            show_status
            ;;
        --kill)
            stop_servers
            ;;
        --logs)
            tail_logs "${2:-50}"
            ;;
        --tail)
            follow_logs
            ;;
        --old)
            if stop_servers; then
                start_original_server
            else
                log "❌ Failed to stop existing servers" "$RED"
                exit 1
            fi
            ;;
        "")
            if stop_servers; then
                start_modular_server
            else
                log "❌ Failed to stop existing servers" "$RED"
                exit 1
            fi
            ;;
        *)
            log "❌ Unknown option: $1" "$RED"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"