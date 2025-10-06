# MCP HTTP Template Server

A clean, professional template for building MCP (Model Context Protocol) servers using streamable HTTP transport. This template is based on the official [simple-streamablehttp example](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-streamablehttp) from the MCP Python SDK.

## Features

- ✅ **Low-level MCP Server implementation** - Uses the official MCP Python SDK's low-level server
- ✅ **Streamable HTTP transport** - Full support for HTTP-based MCP communication
- ✅ **Resumability support** - Built-in event store for connection resumption
- ✅ **Example tools and resources** - Ready-to-use examples you can extend
- ✅ **Professional structure** - Clean, maintainable code organization
- ✅ **Development tools** - Linting, formatting, and testing setup
- ✅ **Easy configuration** - Environment-based configuration management
- ✅ **CORS support** - Ready for browser-based clients

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip or uv for package management

### Installation

1. **Clone or download this template:**
   ```bash
   git clone https://github.com/raihan0824/mcp-http-template.git
   cd mcp-http-template
   ```

2. **Install dependencies:**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using uv (recommended)
   uv sync
   ```

3. **Run the server:**
   ```bash
   python -m mcp_server.main
   ```

   The server will start on `http://127.0.0.1:3000` by default.

### Using Make (Optional)

This template includes a Makefile for common tasks:

```bash
# Install dependencies
make install

# Install development dependencies
make install-dev

# Run the server
make run

# Format code
make format

# Run linting
make lint

# Run type checking
make type-check
```

## Configuration

### Command Line Options

```bash
python -m mcp_server.main --help

Options:
  --port INTEGER          Port to listen on for HTTP (default: 3000)
  --log-level TEXT        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --json-response         Enable JSON responses instead of SSE streams
  --help                  Show this message and exit.
```

### Environment Variables

Copy `env.example` to `.env` and modify as needed:

```bash
cp env.example .env
```

Available environment variables:
- `MCP_SERVER_NAME` - Server name (default: "MCP HTTP Template Server")
- `MCP_HOST` - Host to bind to (default: "localhost")
- `MCP_PORT` - Port to listen on (default: 8000)
- `MCP_LOG_LEVEL` - Logging level (default: "INFO")
- `MCP_ENABLE_TOOLS` - Enable tools (default: "true")
- `MCP_ENABLE_RESOURCES` - Enable resources (default: "true")
- `MCP_ENABLE_PROMPTS` - Enable prompts (default: "true")

## Available Tools

The template includes several example tools:

### 1. `greet`
Greet someone by name.
```json
{
  "name": "greet",
  "arguments": {
    "name": "Alice"
  }
}
```

### 2. `calculate`
Perform basic mathematical calculations.
```json
{
  "name": "calculate",
  "arguments": {
    "operation": "add",
    "a": 5,
    "b": 3
  }
}
```

### 3. `get_server_info`
Get information about the server.
```json
{
  "name": "get_server_info",
  "arguments": {}
}
```

### 4. `send_notification`
Send a stream of notifications (demonstrates streaming capabilities).
```json
{
  "name": "send_notification",
  "arguments": {
    "interval": 1.0,
    "count": 3,
    "caller": "test-client"
  }
}
```

## Available Resources

### 1. `server://status`
Get the current server status.

### 2. `server://config`
Get the current server configuration.

## Testing the Server

### Using curl

1. **Test basic connectivity:**
   ```bash
   curl -X POST http://127.0.0.1:3000/mcp \\
     -H "Content-Type: application/json" \\
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
   ```

2. **Call a tool:**
   ```bash
   curl -X POST http://127.0.0.1:3000/mcp \\
     -H "Content-Type: application/json" \\
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/call",
       "params": {
         "name": "greet",
         "arguments": {"name": "World"}
       }
     }'
   ```

3. **List resources:**
   ```bash
   curl -X POST http://127.0.0.1:3000/mcp \\
     -H "Content-Type: application/json" \\
     -d '{"jsonrpc": "2.0", "id": 1, "method": "resources/list"}'
   ```

### Using an MCP Client

This server is compatible with any MCP client that supports the streamable HTTP transport. The server endpoint is:

```
http://127.0.0.1:3000/mcp
```

## Customizing the Template

### Adding New Tools

1. **Add your tool handler in `mcp_server/main.py`:**
   ```python
   elif name == "your_tool_name":
       # Your tool logic here
       result = "Your result"
       return [types.TextContent(type="text", text=result)]
   ```

2. **Add the tool definition to `list_tools()`:**
   ```python
   types.Tool(
       name="your_tool_name",
       description="Description of your tool",
       inputSchema={
           "type": "object",
           "required": ["param1"],
           "properties": {
               "param1": {
                   "type": "string",
                   "description": "Parameter description"
               }
           }
       }
   )
   ```

### Adding New Resources

1. **Add the resource to `list_resources()`:**
   ```python
   types.Resource(
       uri=AnyUrl("your://resource"),
       name="Your Resource",
       description="Description of your resource",
       mimeType="text/plain"
   )
   ```

2. **Handle the resource in `read_resource()`:**
   ```python
   elif str(uri) == "your://resource":
       return "Your resource content"
   ```

## Development

### Code Formatting

This template uses Black and isort for code formatting:

```bash
# Format code
make format

# Check formatting
make lint
```

### Type Checking

Type checking is done with mypy:

```bash
make type-check
```

### Project Structure

```
mcp-http-template/
├── mcp_server/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Main server implementation
│   └── config.py            # Configuration management
├── tests/
│   └── __init__.py          # Tests package
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── Makefile                # Development commands
├── env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Production Deployment

### Important Notes

1. **Event Store**: The included `InMemoryEventStore` is for demonstration only. For production, implement a persistent event store (Redis, database, etc.).

2. **Security**: Update CORS settings in production:
   ```python
   starlette_app = CORSMiddleware(
       starlette_app,
       allow_origins=["https://yourdomain.com"],  # Specific origins
       allow_methods=["GET", "POST", "DELETE"],
       expose_headers=["Mcp-Session-Id"],
   )
   ```

3. **Logging**: Configure appropriate logging levels and handlers for production.

4. **Error Handling**: Add comprehensive error handling for your specific use cases.

## License

This template is provided under the MIT License. See the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For questions about MCP:
- [MCP Documentation](https://model-context-protocol.com/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

For issues with this template:
- Open an issue in this repository
- Check the existing issues for similar problems

---

**Happy coding! 🚀**
