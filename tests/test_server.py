"""Basic tests for the MCP HTTP Template Server."""

import pytest
from mcp_server.main import app, InMemoryEventStore


class TestInMemoryEventStore:
    """Test the InMemoryEventStore class."""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_events(self):
        """Test storing and retrieving events."""
        store = InMemoryEventStore()
        stream_id = "test_stream"
        
        # Store some events
        event_id1 = await store.store_event(stream_id, {"method": "test1", "data": "data1"})
        event_id2 = await store.store_event(stream_id, {"method": "test2", "data": "data2"})
        event_id3 = await store.store_event(stream_id, {"method": "test3", "data": "data3"})
        
        # Retrieve all events
        events = await store.get_events_since(stream_id)
        assert len(events) == 3
        assert events[0]["id"] == event_id1
        assert events[0]["message"]["data"] == "data1"
        
        # Retrieve events since event1
        events = await store.get_events_since(stream_id, event_id1)
        assert len(events) == 2
        assert events[0]["id"] == event_id2
        
        # Retrieve events for non-existent session
        events = await store.get_events_since("non_existent")
        assert len(events) == 0


class TestMCPServer:
    """Test the MCP server functionality."""
    
    def test_server_initialization(self):
        """Test that the server initializes correctly."""
        assert app.name == "MCP HTTP Template Server"
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        # This would require more setup to properly test the async handlers
        # For now, just verify the server object exists
        assert app is not None
        assert hasattr(app, 'name')
        assert app.name == "MCP HTTP Template Server"
