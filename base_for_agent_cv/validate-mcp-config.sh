#!/bin/bash
# validate-mcp-config.sh
# Validates the .mcp.json configuration file structure

set -e

MCP_CONFIG=".mcp.json"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install jq to validate JSON."
    echo "On Ubuntu/Debian: sudo apt-get install jq"
    echo "On macOS: brew install jq"
    exit 1
fi

# Check if .mcp.json exists
if [ ! -f "$MCP_CONFIG" ]; then
    echo "Error: $MCP_CONFIG file not found."
    exit 1
fi

# Validate JSON syntax
if ! jq empty "$MCP_CONFIG" 2>/dev/null; then
    echo "Error: $MCP_CONFIG contains invalid JSON."
    exit 1
fi

# Check for required fields
if ! jq -e '.mcpServers' "$MCP_CONFIG" > /dev/null 2>&1; then
    echo "Error: $MCP_CONFIG is missing 'mcpServers' field."
    exit 1
fi

if ! jq -e '.mcpServers.context7' "$MCP_CONFIG" > /dev/null 2>&1; then
    echo "Error: $MCP_CONFIG is missing 'mcpServers.context7' configuration."
    exit 1
fi

if ! jq -e '.mcpServers.context7.command' "$MCP_CONFIG" > /dev/null 2>&1; then
    echo "Error: 'mcpServers.context7.command' is missing."
    exit 1
fi

if ! jq -e '.mcpServers.context7.args' "$MCP_CONFIG" > /dev/null 2>&1; then
    echo "Error: 'mcpServers.context7.args' is missing."
    exit 1
fi

# Check if the version is pinned (not using @latest)
ARGS=$(jq -r '.mcpServers.context7.args[]' "$MCP_CONFIG")
if echo "$ARGS" | grep -q "@latest"; then
    echo "Warning: Using @latest in args. Consider pinning to a specific version."
fi

# Check if version is pinned
if echo "$ARGS" | grep -E '@[0-9]+\.[0-9]+\.[0-9]+' > /dev/null; then
    echo "✓ MCP configuration is valid."
    echo "✓ Version is pinned: $(echo "$ARGS" | grep -oE '@[0-9]+\.[0-9]+\.[0-9]+')"
else
    echo "Warning: Version does not appear to be pinned to a specific semver version."
fi

echo "✓ All required fields are present in $MCP_CONFIG"
exit 0
