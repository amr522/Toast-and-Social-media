#!/bin/bash

echo "🚀 Setting up Combined MCP Servers (Context7 + MiniMax)"
echo "======================================================"

# Check if .env file exists and load MiniMax API key
if [ -f "../.env" ]; then
    echo "📄 Loading environment variables from .env file..."
    # Extract MINIMAX_API_KEY from .env file
    MINIMAX_API_KEY=$(grep "^MINIMAX_API_KEY=" ../.env | cut -d '=' -f2- | sed 's/^"//' | sed 's/"$//')
    if [ -n "$MINIMAX_API_KEY" ]; then
        export MINIMAX_API_KEY="$MINIMAX_API_KEY"
        echo "✅ MiniMax API key loaded from .env file"
    else
        echo "⚠️  MINIMAX_API_KEY not found in .env file"
        echo "   Please ensure it's defined in ../.env"
        exit 1
    fi
else
    echo "⚠️  .env file not found in parent directory"
    echo "   Please create ../.env with MINIMAX_API_KEY"
    exit 1
fi

echo ""
echo "🧪 Testing MCP Servers..."

# Test Context7
echo "Testing Context7 MCP..."
if npx -y @upstash/context7-mcp --help &> /dev/null; then
    echo "✅ Context7 MCP server accessible"
else
    echo "⚠️  Context7 MCP server not accessible"
fi

# Test MiniMax with API key
echo "Testing MiniMax MCP..."
if MINIMAX_API_KEY="$MINIMAX_API_KEY" npx -y minimax-mcp-js --help &> /dev/null; then
    echo "✅ MiniMax MCP server accessible"
else
    echo "⚠️  MiniMax MCP server not accessible"
    echo "   Check API key validity and network connection"
fi

echo ""
echo "📋 Configuration Summary:"
echo "   - Combined config: .mcp/combined-config.json"
echo "   - API Key: Loaded from ../.env"
echo "   - Output directory: /Users/Heidak/Downloads/Toast-and-Social-media-main/build"
echo ""
echo "🚀 Next Steps:"
echo "   1. Configure your MCP client (VS Code/Cursor/Claude Desktop) with combined-config.json"
echo "   2. Both servers will be available for documentation + content generation"
echo "   3. Use 'use context7' for docs, MiniMax commands for content generation"