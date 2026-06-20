#!/usr/bin/env bash
# Setup script for Unraid MCP Plugin
# Installs the MCP server dependencies

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$PLUGIN_ROOT/../.." && pwd)"

echo "=== Unraid MCP Plugin Setup ==="
echo ""
echo "Plugin root: $PLUGIN_ROOT"
echo "Project root: $PROJECT_ROOT"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed."
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv is installed"

# Navigate to project root and install dependencies
cd "$PROJECT_ROOT"

echo "Installing Python dependencies..."
uv sync

echo ""
echo "✓ Setup complete!"
echo ""
echo "Configure your Unraid server by setting these environment variables:"
echo "  export UNRAID_API_URL='http://your-unraid-server/graphql'"
echo "  export UNRAID_API_KEY='your-api-key'"
echo ""
echo "Test the MCP server with:"
echo "  uv run unraid-mcp-server"
