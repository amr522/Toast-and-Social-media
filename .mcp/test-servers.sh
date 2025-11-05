#!/bin/bash

echo "🔍 Testing Combined MCP Server Setup"
echo "===================================="

# Test Context7 MCP
echo "🧪 Testing Context7 MCP Server..."
if npx -y @upstash/context7-mcp --help &> /dev/null; then
    echo "✅ Context7 MCP server is accessible"
else
    echo "⚠️  Context7 MCP server not accessible (may need installation)"
fi

# Test MiniMax MCP (with embedded API key from config)
echo ""
echo "🧪 Testing MiniMax MCP Server..."
if uvx minimax-mcp --help &> /dev/null; then
    echo "✅ MiniMax MCP server is accessible"
    echo "   API key configured in combined-config.json"
else
    echo "⚠️  MiniMax MCP server not accessible"
    echo "   Check uvx installation and network connectivity"
fi

echo ""
echo "📋 Configuration Files:"
echo "   - Combined config: .mcp/combined-config.json"
echo "   - MiniMax only: .mcp/project-config.json"
echo "   - Context7 only: Available via VS Code extension"
echo ""
echo "🚀 To use both servers together:"
echo "   1. Install Context7 VS Code extension"
echo "   2. Configure MCP client with combined-config.json"
echo "   3. Use 'use context7' for documentation + MiniMax for content generation"