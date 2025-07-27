#!/bin/bash
# Wrapper script for MCP server to handle paths with spaces

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include the project directory
export PYTHONPATH="$SCRIPT_DIR"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists and use it
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    echo "🐍 Using virtual environment Python" >&2
    exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/mcp_server_standalone.py"
elif command -v uv >/dev/null 2>&1; then
    echo "📦 Using UV to run server" >&2
    exec uv run python "$SCRIPT_DIR/mcp_server.py"
else
    echo "🔧 Using system Python" >&2
    exec python3 "$SCRIPT_DIR/mcp_server_standalone.py"
fi
