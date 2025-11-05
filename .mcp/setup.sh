#!/bin/bash

echo "🍽️  MiniMax MCP Server Setup for Toast & Social Media Pipeline"
echo "============================================================"

# Check if MiniMax API key is set
if [ -z "$MINIMAX_API_KEY" ]; then
    echo "⚠️  MINIMAX_API_KEY environment variable is not set"
    echo "   Please set it with: export MINIMAX_API_KEY='your_api_key_here'"
    echo "   Get your API key from: https://platform.minimax.io/user-center/basic-information/interface-key"
    exit 1
else
    echo "✅ MiniMax API key is configured"
fi

# Create necessary directories
echo "📁 Creating output directories..."
mkdir -p build/audio
mkdir -p build/enhanced_images
mkdir -p build/videos
mkdir -p build/music
mkdir -p build/content
echo "✅ Output directories created"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "⚠️  MiniMax MCP server package not available yet."
echo "   Configuration files are ready for when the package is published."
echo ""
echo "📋 Next steps:"
echo "1. Monitor MiniMax GitHub repos for package availability:"
echo "   - Python: https://github.com/MiniMax-AI/MiniMax-MCP"
echo "   - JavaScript: https://github.com/MiniMax-AI/MiniMax-MCP-JS"
echo "2. Once available, install with one of:"
echo "   - uvx minimax-mcp (if published)"
echo "   - pip install git+https://github.com/MiniMax-AI/MiniMax-MCP.git"
echo "   - npm install -g minimax-mcp-js"
echo "3. Configure your MCP client with .mcp/project-config.json"
echo ""
echo "🔧 Available tools (when MCP server is available):"
echo "   - text_to_audio: Convert text to speech"
echo "   - text_to_image: Generate images from prompts"
echo "   - generate_video: Create videos from descriptions"
echo "   - music_generation: Compose music with lyrics"
echo "   - voice_clone: Clone voices from audio files"
echo ""
echo "📖 For more information, see: .mcp/README.md"
