"""
Configuration module for the MCP HTTP Template Server.

This module provides configuration management for the MCP server,
including environment variables, logging setup, and server settings.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging


@dataclass
class ServerConfig:
    """Configuration class for the MCP server."""
    
    # Server settings
    name: str = "MCP HTTP Template Server"
    version: str = "0.1.0"
    description: str = "A clean, professional template for building MCP servers"
    
    # Transport settings
    transport: str = "streamable-http"
    host: str = "localhost"
    port: int = 8000
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature flags
    enable_tools: bool = True
    enable_resources: bool = True
    enable_prompts: bool = True
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """
        Create configuration from environment variables.
        
        Returns:
            ServerConfig instance with values from environment variables
        """
        return cls(
            name=os.getenv("MCP_SERVER_NAME", cls.name),
            host=os.getenv("MCP_HOST", cls.host),
            port=int(os.getenv("MCP_PORT", str(cls.port))),
            log_level=os.getenv("MCP_LOG_LEVEL", cls.log_level),
            enable_tools=os.getenv("MCP_ENABLE_TOOLS", "true").lower() == "true",
            enable_resources=os.getenv("MCP_ENABLE_RESOURCES", "true").lower() == "true",
            enable_prompts=os.getenv("MCP_ENABLE_PROMPTS", "true").lower() == "true",
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "transport": self.transport,
            "host": self.host,
            "port": self.port,
            "log_level": self.log_level,
            "enable_tools": self.enable_tools,
            "enable_resources": self.enable_resources,
            "enable_prompts": self.enable_prompts,
        }
    
    def setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=self.log_format
        )


# Global configuration instance
config = ServerConfig.from_env()
