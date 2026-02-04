#!/bin/bash

# Unraid MCP Server Development Script
# Safely manages server processes during development with accurate process detection

set -euo pipefail

# Configuration
DEFAULT_PORT=6970
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="/tmp"
LOG_FILE="$LOG_DIR/unraid-mcp.log"
PID_FILE="$LOG_DIR/dev.pid"
# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# All colors are now handled by Rich logging system

# Helper function for unified Rich logging
log() {
    local message="$1"
    local level="${2:-info}"
    local indent="${3:-0}"
    local file_timestamp="$(date +'%Y-%m-%d %H:%M:%S')"
    
    # Use unified Rich logger for beautiful console output - use env vars to avoid injection
    export LOG_MESSAGE="$message"
    export LOG_LEVEL="$level"
    export LOG_INDENT="$indent"
    
    uv run python -c "import os; from unraid_mcp.config.logging import log_with_level_and_indent; log_with_level_and_indent(os.environ.get('LOG_MESSAGE', ''), os.environ.get('LOG_LEVEL', 'info'), int(os.environ.get('LOG_INDENT', 0)))"
    
    # Unset env vars
    unset LOG_MESSAGE LOG_LEVEL LOG_INDENT
    
    # File output without color
    printf "[%s] %s\n" "$file_timestamp" "$message" >> "$LOG_FILE"
}

# Convenience functions for different log levels
log_error() { log "$1" "error" "${2:-0}"; }
log_warning() { log "$1" "warning" "${2:-0}"; }
log_success() { log "$1" "success" "${2:-0}"; }
log_info() { log "$1" "info" "${2:-0}"; }
log_status() { log "$1" "status" "${2:-0}"; }

# Rich header function
log_header() {
    uv run python -c "from unraid_mcp.config.logging import log_header; log_header('$1')"
}

# Rich separator function  
log_separator() {
    uv run python -c "from unraid_mcp.config.logging import log_separator; log_separator()"
}

# Get port from environment or use default
get_port() {
    local port="${UNRAID_MCP_PORT:-$DEFAULT_PORT}"
    echo "$port"
}

# Write PID to file
write_pid_file() {
    local pid=$1
    echo "$pid" > "$PID_FILE"
}

# Read PID from file
read_pid_file() {
    if [[ -f "$PID_FILE" ]]; then
        cat "$PID_FILE" 2>/dev/null
    fi
}

# Check if PID file contains valid running process
is_pid_valid() {
    local pid=$1
    [[ -n "$pid" ]] && [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null
}

# Clean up PID file
cleanup_pid_file() {
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
        log_info "🗑️  Cleaned up PID file"
    fi
}

# Get PID from PID file if valid, otherwise return empty
get_valid_pid_from_file() {
    local pid=$(read_pid_file)
    if is_pid_valid "$pid"; then
        echo "$pid"
    else
        # Clean up stale PID file
        [[ -f "$PID_FILE" ]] && cleanup_pid_file
        echo ""
    fi
}

# Find processes using multiple detection methods
find_server_processes() {
    local port=$(get_port)
    local pids=()
    
    # Method 0: Check PID file first (most reliable)
    local pid_from_file=$(get_valid_pid_from_file)
    if [[ -n "$pid_from_file" ]]; then
        log_status "🔍 Found server PID from file: $pid_from_file"
        pids+=("$pid_from_file")
    fi
    
    # Method 1: Command line pattern matching (fallback)
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            local pid=$(echo "$line" | awk '{print $2}')
            # Add to pids if not already present
            if [[ ! " ${pids[@]:-} " =~ " $pid " ]]; then
                pids+=("$pid")
            fi
        fi
    done < <(ps aux | grep -E 'python.*unraid.*mcp|python.*main\.py|uv run.*main\.py|uv run -m unraid_mcp' | grep -v grep | grep -v "$0")
    
    # Method 2: Port binding verification (fallback)
    if command -v lsof >/dev/null 2>&1; then
        while IFS= read -r line; do
            if [[ -n "$line" ]]; then
                local pid=$(echo "$line" | awk '{print $2}')
                # Add to pids if not already present
                if [[ ! " ${pids[@]:-} " =~ " $pid " ]]; then
                    pids+=("$pid")
                fi
            fi
        done < <(lsof -i ":$port" 2>/dev/null | grep LISTEN || true)
    fi
    
    # Method 3: Working directory verification for fallback methods
    local verified_pids=()
    for pid in "${pids[@]}"; do
        # Skip if not a valid PID
        if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
            continue
        fi
        
        # If this PID came from the PID file, it's already verified
        if [[ "$pid" == "$pid_from_file" ]]; then
            verified_pids+=("$pid")
            continue
        fi
        
        # Verify other PIDs by working directory
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
        log_warning "⚠️  Process $pid ($name) already terminated"
        return 0
    fi
    
    log_warning "🔄 Terminating $name (PID: $pid)..."
    
    # Step 1: Graceful shutdown (SIGTERM)
    log_info "→ Sending SIGTERM to PID $pid" 1
    kill -TERM "$pid" 2>/dev/null || {
        log_warning "⚠️  Failed to send SIGTERM (process may have died)" 2
        return 0
    }
    
    # Step 2: Wait for graceful shutdown (5 seconds)
    local count=0
    while [[ $count -lt 5 ]]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            log_success "✅ Process $pid terminated gracefully" 1
            
            # Clean up PID file if this was our server process
            local pid_from_file=$(read_pid_file)
            if [[ "$pid" == "$pid_from_file" ]]; then
                cleanup_pid_file
            fi
            
            return 0
        fi
        sleep 1
        ((count++))
        log_info "⏳ Waiting for graceful shutdown... (${count}/5)" 2
    done
    
    # Step 3: Force kill (SIGKILL)
    log_error "⚡ Graceful shutdown timeout, sending SIGKILL to PID $pid" 1
    kill -KILL "$pid" 2>/dev/null || {
        log_warning "⚠️  Failed to send SIGKILL (process may have died)" 2
        return 0
    }
    
    # Step 4: Final verification
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
        log_error "❌ Failed to terminate process $pid" 1
        return 1
    else
        log_success "✅ Process $pid terminated forcefully" 1
        
        # Clean up PID file if this was our server process
        local pid_from_file=$(read_pid_file)
        if [[ "$pid" == "$pid_from_file" ]]; then
            cleanup_pid_file
        fi
        
        return 0
    fi
}

# Stop all server processes
stop_servers() {
    log_header "Server Shutdown"
    log_error "🛑 Stopping existing server processes..."
    
    local pids=($(find_server_processes))
    
    if [[ ${#pids[@]} -eq 0 ]]; then
        log_success "✅ No processes to stop"
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
    log_info "⏳ Waiting for port $port to be released..."
    local port_wait=0
    while [[ $port_wait -lt 3 ]]; do
        if command -v lsof >/dev/null 2>&1; then
            if ! lsof -i ":$port" >/dev/null 2>&1; then
                log_success "✅ Port $port released" 1
                break
            fi
        else
             # Fallback if lsof is missing: assume success or check netstat (omitted for simplicity, just breaking loop)
             # Realistically if lsof is missing we can't easily check, so we trust kill worked or wait blindly.
             # For now, just break since we can't verify.
             log_warning "⚠️  lsof not found, skipping port release check" 1
             break
        fi
        sleep 1
        ((port_wait++))
    done
    
    if [[ $failed -gt 0 ]]; then
        log_error "⚠️  Failed to stop $failed process(es)"
        return 1
    else
        log_success "✅ All processes stopped successfully"
        return 0
    fi
}

# Start the new modular server
start_modular_server() {
    log_header "Modular Server Startup"
    log_success "🚀 Starting modular server..."
    
    cd "$PROJECT_DIR"
    
    # Check if main.py exists in unraid_mcp/
    if [[ ! -f "unraid_mcp/main.py" ]]; then
        log_error "❌ unraid_mcp/main.py not found. Make sure modular server is implemented."
        return 1
    fi
    
    # Clear the log file and add a startup marker to capture fresh logs
    # Rotate logs if too large (e.g., >10MB) or just simple rotation
    if [[ -f "$LOG_FILE" ]]; then
        local fsize=$(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0)
        if [[ $fsize -gt 10485760 ]]; then # 10MB
            mv "$LOG_FILE" "$LOG_FILE.old"
        fi
    fi
    
    # Append startup marker
    echo "=== Server Starting at $(date) ===" >> "$LOG_FILE"
    
    # Start server in background using module syntax
    log_info "→ Executing: uv run -m unraid_mcp.main" 1
    # Start server in new process group to isolate it from parent signals
    # Start server in new process group to isolate it from parent signals
    # Use setsid to detach, but tracking the PID is tricky.
    # New approach: Run in background and find the child PID.
    setsid nohup uv run -m unraid_mcp.main >> "$LOG_FILE" 2>&1 &
    local shell_pid=$!
    
    # Wait for the python process to appear
    local attempts=0
    local pid=""
    while [[ $attempts -lt 20 && -z "$pid" ]]; do
        sleep 0.1
        # Try to find the child process of the shell_pid or the setsid process
        # This is tricky because setsid executes the program. 
        # Actually setsid execs, so the shell_pid should be the pid of setsid which becomes the pid of uv which becomes... 
        # Wait, setsid forks? No, setsid command runs a program in a new session.
        # If we used `setsid program &`, $! is the pid of `setsid`. 
        # If `setsid` execs, then $! is the PID we want.
        # But `uv run` might spawn python as a child. 
        # Let's try to match by command line as requested by user fallback.
        
        # Look for the python process running unraid_mcp.main
        pid=$(pgrep -f "unraid_mcp.main" | sort -n | tail -1)
        
        # Verify it's new (not an old one we failed to kill) - risky if improper cleanup, but we did cleanup.
        ((attempts++))
    done
    
    if [[ -z "$pid" ]]; then
       # Fallback to the shell PID if we can't find specific python one, though it might be wrong.
       pid=$shell_pid
    fi
    
    # Write PID to file
    write_pid_file "$pid"
    log_info "📝 Written PID $pid to file: $PID_FILE" 1
    
    # Give it a moment to start and write some logs
    sleep 3
    
    # Check if it's still running
    if kill -0 "$pid" 2>/dev/null; then
        local port=$(get_port)
        log_success "✅ Modular server started successfully (PID: $pid, Port: $port)"
        log_info "📋 Process info: $(ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null || echo 'Process info unavailable')" 1
        
        # Auto-tail logs after successful start
        echo ""
        log_success "📄 Following server logs in real-time..."
        log_info "ℹ️  Press Ctrl+C to stop following logs (server will continue running)" 1
        log_separator
        echo ""
        
        # Set up signal handler for graceful exit from log following
        trap 'handle_log_interrupt' SIGINT
        
        # Start tailing from beginning of the fresh log file
        tail -f "$LOG_FILE"
        
        return 0
    else
        log_error "❌ Modular server failed to start"
        cleanup_pid_file
        log_warning "📄 Check $LOG_FILE for error details"
        return 1
    fi
}

# Start the original server
start_original_server() {
    log_header "Original Server Startup"
    log_success "🚀 Starting original server..."
    
    cd "$PROJECT_DIR"
    
    # Check if original server exists
    if [[ ! -f "unraid_mcp_server.py" ]]; then
        log_error "❌ unraid_mcp_server.py not found"
        return 1
    fi
    
    # Clear the log file and add a startup marker to capture fresh logs
    # Rotate logs if too large (e.g., >10MB) or just simple rotation
    if [[ -f "$LOG_FILE" ]]; then
        local fsize=$(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0)
        if [[ $fsize -gt 10485760 ]]; then # 10MB
            mv "$LOG_FILE" "$LOG_FILE.old"
        fi
    fi
    
    # Append startup marker
    echo "=== Server Starting at $(date) ===" >> "$LOG_FILE"
    
    # Start server in background
    log_info "→ Executing: uv run unraid_mcp_server.py" 1
    # Start server in new process group to isolate it from parent signals
    # Use setsid to detach, but tracking the PID is tricky.
    # New approach: Run in background and find the child PID.
    setsid nohup uv run unraid_mcp_server.py >> "$LOG_FILE" 2>&1 &
    local shell_pid=$!
    
    # Wait for the python process to appear
    local attempts=0
    local pid=""
    while [[ $attempts -lt 20 && -z "$pid" ]]; do
        sleep 0.1
        # Look for the python process running unraid_mcp_server.py
        pid=$(pgrep -f "unraid_mcp_server.py" | sort -n | tail -1)
        ((attempts++))
    done
    
    if [[ -z "$pid" ]]; then
       # Fallback to the shell PID if we can't find specific python one
       pid=$shell_pid
    fi
    
    # Write PID to file
    write_pid_file "$pid"
    log_info "📝 Written PID $pid to file: $PID_FILE" 1
    
    # Give it a moment to start and write some logs
    sleep 3
    
    # Check if it's still running
    if kill -0 "$pid" 2>/dev/null; then
        local port=$(get_port)
        log_success "✅ Original server started successfully (PID: $pid, Port: $port)"
        log_info "📋 Process info: $(ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null || echo 'Process info unavailable')" 1
        
        # Auto-tail logs after successful start
        echo ""
        log_success "📄 Following server logs in real-time..."
        log_info "ℹ️  Press Ctrl+C to stop following logs (server will continue running)" 1
        log_separator
        echo ""
        
        # Set up signal handler for graceful exit from log following
        trap 'handle_log_interrupt' SIGINT
        
        # Start tailing from beginning of the fresh log file
        tail -f "$LOG_FILE"
        
        return 0
    else
        log_error "❌ Original server failed to start"
        cleanup_pid_file
        log_warning "📄 Check $LOG_FILE for error details"
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
    echo "  ./scripts/dev.sh              # Restart with modular server"
    echo "  ./scripts/dev.sh --old        # Restart with original server"
    echo "  ./scripts/dev.sh --kill       # Stop all servers"
    echo "  ./scripts/dev.sh --status     # Check server status"
    echo "  ./scripts/dev.sh --logs       # Show last 50 lines of logs"
    echo "  ./scripts/dev.sh --logs 100   # Show last 100 lines of logs"
    echo "  ./scripts/dev.sh --tail       # Follow logs in real-time"
}

# Show server status
show_status() {
    local port=$(get_port)
    log_header "Server Status"
    log_status "🔍 Server Status Check"
    log_info "📁 Project Directory: $PROJECT_DIR" 1
    log_info "📝 PID File: $PID_FILE" 1
    log_info "🔌 Expected Port: $port" 1
    echo ""
    
    # Check PID file status
    local pid_from_file=$(read_pid_file)
    if [[ -n "$pid_from_file" ]]; then
        if is_pid_valid "$pid_from_file"; then
            log_success "✅ PID File: Contains valid PID $pid_from_file" 1
        else
            log_warning "⚠️  PID File: Contains stale PID $pid_from_file (process not running)" 1
        fi
    else
        log_warning "🚫 PID File: Not found or empty" 1
    fi
    echo ""
    
    local pids=($(find_server_processes))
    
    if [[ ${#pids[@]} -eq 0 ]]; then
        log_warning "🟡 Status: No servers running" 1
    else
        log_success "✅ Status: ${#pids[@]} server(s) running" 1
        for pid in "${pids[@]}"; do
            local cmd=$(ps -p "$pid" -o cmd --no-headers 2>/dev/null || echo "Command unavailable")
            local source="process scan"
            if [[ "$pid" == "$pid_from_file" ]]; then
                source="PID file"
            fi
            log_success "PID $pid ($source): $cmd" 2
        done
    fi
    
    # Check port binding
    if command -v lsof >/dev/null 2>&1; then
        local port_info=$(lsof -i ":$port" 2>/dev/null | grep LISTEN || echo "")
        if [[ -n "$port_info" ]]; then
            log_success "Port $port: BOUND" 1
            echo "$port_info" | while IFS= read -r line; do
                log_info "$line" 2
            done
        else
            log_warning "Port $port: FREE" 1
        fi
    fi
}

# Tail the server logs
tail_logs() {
    local lines="${1:-50}"
    
    log_info "📄 Tailing last $lines lines from server logs..."
    
    if [[ ! -f "$LOG_FILE" ]]; then
        log_error "❌ Log file not found: $LOG_FILE"
        return 1
    fi
    
    echo ""
    echo "=== Server Logs (last $lines lines) ==="
    tail -n "$lines" "$LOG_FILE"
    echo "=== End of Logs ===="
    echo ""
}

# Handle SIGINT during log following
handle_log_interrupt() {
    echo ""
    log_info "📄 Stopped following logs. Server continues running in background."
    log_info "💡 Use './dev.sh --status' to check server status" 1
    log_info "💡 Use './dev.sh --tail' to resume following logs" 1
    exit 0
}

# Follow server logs in real-time
follow_logs() {
    log_success "📄 Following server logs in real-time..."
    log_info "ℹ️  Press Ctrl+C to stop following logs"
    
    if [[ ! -f "$LOG_FILE" ]]; then
        log_error "❌ Log file not found: $LOG_FILE"
        return 1
    fi
    
    # Set up signal handler for graceful exit
    trap 'handle_log_interrupt' SIGINT
    
    log_separator
    echo ""
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
                log_error "❌ Failed to stop existing servers"
                exit 1
            fi
            ;;
        "")
            if stop_servers; then
                start_modular_server
            else
                log_error "❌ Failed to stop existing servers"
                exit 1
            fi
            ;;
        *)
            log_error "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"