#!/usr/bin/env python3
"""
MCP HTTP Server Template

A simple, clean implementation of an MCP server using streamable HTTP transport.
Based on the official simple-streamablehttp example from the MCP Python SDK.

This template provides:
- Basic server setup with low-level MCP Server
- Example tools and resources
- Clean, extensible structure
- Professional error handling
- Streamable HTTP transport with resumability
"""

import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any, Dict, List

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pydantic import AnyUrl
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the MCP server
app = Server("MCP HTTP Template Server")


# Tool implementations
@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    """Handle tool calls."""
    ctx = app.request_context
    
    if name == "greet":
        name_arg = arguments.get("name", "World")
        logger.info(f"Greeting {name_arg}")
        result = f"Hello, {name_arg}! Welcome to the MCP HTTP Template Server."
        return [types.TextContent(type="text", text=result)]
    
    elif name == "calculate":
        operation = arguments.get("operation")
        a = arguments.get("a")
        b = arguments.get("b")
        
        logger.info(f"Calculating {a} {operation} {b}")
        
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else None
        }
        
        if operation not in operations:
            error_msg = f"Unknown operation: {operation}. Valid operations: {list(operations.keys())}"
            return [types.TextContent(type="text", text=error_msg)]
        
        if operation == "divide" and b == 0:
            error_msg = "Division by zero is not allowed"
            return [types.TextContent(type="text", text=error_msg)]
        
        result = operations[operation](a, b)
        result_msg = f"Result: {a} {operation} {b} = {result}"
        return [types.TextContent(type="text", text=result_msg)]
    
    elif name == "get_server_info":
        info = {
            "name": "MCP HTTP Template Server",
            "version": "0.1.0",
            "description": "A clean, professional template for building MCP servers",
            "transport": "streamable-http",
            "available_tools": ["greet", "calculate", "get_server_info", "send_notification"],
            "status": "running"
        }
        return [types.TextContent(type="text", text=str(info))]
    
    elif name == "send_notification":
        # Example of sending notifications (like in the original example)
        interval = arguments.get("interval", 1.0)
        count = arguments.get("count", 3)
        caller = arguments.get("caller", "unknown")

        # Send the specified number of notifications with the given interval
        for i in range(count):
            notification_msg = f"[{i + 1}/{count}] Notification from '{caller}' - interval: {interval}s"
            await ctx.session.send_log_message(
                level="info",
                data=notification_msg,
                logger="notification_stream",
                related_request_id=ctx.request_id,
            )
            logger.debug(f"Sent notification {i + 1}/{count} for caller: {caller}")
            if i < count - 1:  # Don't wait after the last notification
                await anyio.sleep(interval)

        result_msg = f"Sent {count} notifications with {interval}s interval for caller: {caller}"
        return [types.TextContent(type="text", text=result_msg)]
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="greet",
            description="Greet someone by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet",
                        "default": "World"
                    }
                }
            }
        ),
        types.Tool(
            name="calculate",
            description="Perform basic mathematical calculations",
            inputSchema={
                "type": "object",
                "required": ["operation", "a", "b"],
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                }
            }
        ),
        types.Tool(
            name="get_server_info",
            description="Get information about this MCP server",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="send_notification",
            description="Send a stream of notifications with configurable count and interval",
            inputSchema={
                "type": "object",
                "required": ["interval", "count", "caller"],
                "properties": {
                    "interval": {
                        "type": "number",
                        "description": "Interval between notifications in seconds"
                    },
                    "count": {
                        "type": "number",
                        "description": "Number of notifications to send"
                    },
                    "caller": {
                        "type": "string",
                        "description": "Identifier of the caller to include in notifications"
                    }
                }
            }
        )
    ]


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri=AnyUrl("server://status"),
            name="Server Status",
            description="Current server status",
            mimeType="text/plain"
        ),
        types.Resource(
            uri=AnyUrl("server://config"),
            name="Server Configuration",
            description="Current server configuration",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read a resource."""
    if str(uri) == "server://status":
        return "Server is running and ready to handle requests."
    elif str(uri) == "server://config":
        import json
        config = {
            "transport": "streamable-http",
            "logging_level": "INFO",
            "tools_enabled": True,
            "resources_enabled": True
        }
        return json.dumps(config, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")


# Create a simple in-memory event store for demonstration
class InMemoryEventStore:
    """Simple in-memory event store for demonstration purposes."""
    
    def __init__(self):
        self.events = {}
        self.event_counter = 0
    
    async def store_event(self, stream_id: str, message) -> str:
        """
        Store an event for later retrieval.
        
        Args:
            stream_id: ID of the stream the event belongs to
            message: The JSON-RPC message to store
            
        Returns:
            The generated event ID for the stored event
        """
        self.event_counter += 1
        event_id = f"event_{self.event_counter}"
        
        if stream_id not in self.events:
            self.events[stream_id] = []
        
        self.events[stream_id].append({
            "id": event_id,
            "message": message
        })
        
        return event_id
    
    async def get_events_since(self, stream_id: str, last_event_id: str = None):
        """
        Get events since a specific event ID.
        
        Args:
            stream_id: ID of the stream
            last_event_id: Last event ID received (optional)
            
        Returns:
            List of events since the last event ID
        """
        if stream_id not in self.events:
            return []
        
        events = self.events[stream_id]
        if not last_event_id:
            return events
        
        # Find the index of the last event ID and return events after it
        for i, event in enumerate(events):
            if event["id"] == last_event_id:
                return events[i + 1:]
        
        return events


@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    """Main entry point for the MCP server."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create event store for resumability
    # The InMemoryEventStore enables resumability support for StreamableHTTP transport.
    # It stores SSE events with unique IDs, allowing clients to:
    #   1. Receive event IDs for each SSE message
    #   2. Resume streams by sending Last-Event-ID in GET requests
    #   3. Replay missed events after reconnection
    # Note: This in-memory implementation is for demonstration ONLY.
    # For production, use a persistent storage solution.
    event_store = InMemoryEventStore()

    # Create the session manager with our app and event store
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=event_store,  # Enable resumability
        json_response=json_response,
    )

    # ASGI handler for streamable HTTP connections
    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing session manager lifecycle."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Wrap ASGI application with CORS middleware to expose Mcp-Session-Id header
    # for browser-based clients (ensures 500 errors get proper CORS headers)
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],  # Allow all origins - adjust as needed for production
        allow_methods=["GET", "POST", "DELETE"],  # MCP streamable HTTP methods
        expose_headers=["Mcp-Session-Id"],
    )

    import uvicorn

    logger.info(f"Starting MCP HTTP Template Server on port {port}...")
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0


if __name__ == "__main__":
    main()
