# MiniMax MCP Server Setup + Context7 Integration

This directory contains MCP (Model Context Protocol) server configurations for both MiniMax AI services and Context7 documentation access.

## Overview

Two MCP servers are configured to work together:

### Context7 MCP Server
- **Purpose**: Real-time access to current documentation for thousands of libraries and frameworks
- **Package**: `@upstash/context7-mcp`
- **Use Case**: Get up-to-date documentation, code examples, and best practices
- **Installation**: `npm install -g @upstash/context7-mcp`

### MiniMax MCP Server
- **Purpose**: Multimodal AI content generation (text, image, voice, music, video)
- **Package**: `minimax-mcp-js` (JavaScript implementation)
- **Use Case**: Generate content for your Toast & Social Media pipeline
- **Installation**: `npm install -g minimax-mcp-js` or use `npx -y minimax-mcp-js`

## Combined Usage for Maximum Efficiency

When both MCP servers are active, you can leverage them together for accelerated development:

### Example Workflow
1. **Use Context7** to research best practices: "Show me current React hooks patterns use context7"
2. **Use MiniMax** to generate content: "Create a voiceover script for our Italian restaurant menu"
3. **Combine both** for complete solutions

### Synergistic Development Approach

#### For Your Toast & Social Media Pipeline:
1. **Context7**: Research current best practices for Python libraries, APIs, and frameworks
2. **MiniMax**: Generate multimedia content (images, videos, audio) for your pipeline
3. **Combined**: Build complete features with accurate documentation + generated content

#### Example Prompts:
```
"Show me how to implement async processing in Python for handling multiple menu items use context7"
"Generate a professional food image of our signature pasta dish"
"Create background music for Italian restaurant ambiance"
"Show me current FastAPI patterns for building REST APIs use context7"
"Generate a voiceover script for our menu descriptions"
```

### MCP Client Setup

#### For VS Code with Context7 Extension + MCP Support
1. Install the Context7 VS Code extension
2. Configure MCP servers using `combined-config.json`
3. Both servers will be available in your AI assistant

#### For Claude Desktop
1. Use `combined-config.json` in your `claude_desktop_config.json`
2. Both Context7 and MiniMax servers will be active

#### For Cursor
1. Import `combined-config.json` into Cursor's MCP settings
2. Access both documentation and content generation capabilities

## Configuration Files

### Individual Server Configs
- `minimax-mcp.json` - MiniMax server only
- `project-config.json` - MiniMax with project-specific paths

### Combined Server Config
- `combined-config.json` - Both Context7 and MiniMax servers

### Prerequisites

1. **Install uv (for Python MCP server):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set MiniMax API Key:**
   ```bash
   export MINIMAX_API_KEY="your_api_key_here"
   # Or load from .env file:
   source ../.env  # if MINIMAX_API_KEY is defined there
   ```

3. **Verify installation:**
   ```bash
   uvx --version
   minimax-mcp --help  # Should work if API key is set
   ```

### MCP Server Installation

#### MiniMax MCP (JavaScript)
```bash
# Install globally
npm install -g minimax-mcp-js

# Or use directly with npx
npx -y minimax-mcp-js --help
```

#### Context7 MCP
```bash
# Install globally
npm install -g @upstash/context7-mcp

# Or use directly with npx
npx -y @upstash/context7-mcp --help
```

#### Alternative MiniMax Packages
If the main package doesn't work, try these alternatives:
```bash
# Updated fork
npm install -g @mcpcn/minimax-mcp-js

# Tools-focused version
npm install -g @iflow-mcp/minimax-mcp-tools
```

The script will attempt multiple installation methods and provide guidance if the package isn't available yet.

#### For VS Code with MCP Extension
1. Install an MCP client extension (if available)
2. Point to the configuration file: `.mcp/minimax-mcp.json`

#### For Claude Desktop
1. Open Claude Desktop settings
2. Go to Developer → Edit Config → `claude_desktop_config.json`
3. Add the MiniMax server configuration

#### For Cursor
1. Go to Cursor → Preferences → Cursor Settings → Tools & Integrations → MCP → Add Custom MCP
2. Import the `.mcp/minimax-mcp.json` file

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MINIMAX_API_KEY` | Your MiniMax API key | - | Yes |
| `MINIMAX_MCP_BASE_PATH` | Local directory for generated files | - | Yes |
| `MINIMAX_API_HOST` | API endpoint URL | `https://api.minimax.io` | No |
| `MINIMAX_API_RESOURCE_MODE` | Resource exposure mode (`url` or `local`) | `url` | No |

### Getting an API Key

1. Visit [MiniMax Developer Platform](https://platform.minimax.io/user-center/basic-information/interface-key)
2. Create a new secret key
3. Copy and securely store the API key (shown only once)

## Available Tools

### Audio Tools
- `text_to_audio`: Convert text to natural speech
- `list_voices`: List available voice options
- `voice_clone`: Clone voice from audio file
- `voice_design`: Generate custom voice from description
- `play_audio`: Play audio files

### Generation Tools
- `music_generation`: Create songs with lyrics
- `text_to_image`: Generate images from text prompts
- `generate_video`: Create videos from text descriptions
- `image_to_video`: Convert images to videos
- `query_video_generation`: Check async video generation status

## Usage Examples

### Text-to-Speech
```
Generate a voiceover for: "Welcome to our restaurant, featuring the finest Italian cuisine."
```

### Image Generation
```
Create a professional food photograph of spaghetti carbonara, hyper-realistic, appetizing presentation.
```

### Video Generation
```
Generate a short video showing the preparation of tiramisu dessert, step-by-step, in 4K resolution.
```

### Music Generation
```
Compose background music for an Italian restaurant: warm, ambient, acoustic guitar and piano, relaxing atmosphere.
```

## Project Integration

The MCP server outputs are configured to use the project's `build/` directory structure:

- Audio files: `build/audio/`
- Images: `build/enhanced_images/`
- Videos: `build/videos/`
- Music: `build/music/`

## Troubleshooting

### Common Issues

1. **"spawn uvx ENOENT" error:**
   - Ensure uv is installed and in PATH
   - Use absolute path to uvx if needed

2. **API Key Issues:**
   - Verify API key is correct and active
   - Check API quota limits

3. **Output Directory Issues:**
   - Ensure the base path exists and is writable
   - Check file system permissions

### Transport Modes

- **studio**: Local MCP client integration (default)
- **SSE**: Server-sent events for cloud deployment

## Development

For development and testing of the MCP integration:

```bash
# Test MCP server connection
uvx minimax-mcp --help

# Validate configuration
python -c "import json; json.load(open('.mcp/minimax-mcp.json'))"
```

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Regularly rotate API keys
- Monitor API usage and costs

---

*Last Updated: November 4, 2025*
*MiniMax MCP Version: Latest*</content>
<parameter name="filePath">/Users/Heidak/Downloads/Toast-and-Social-media-main/.mcp/README.md