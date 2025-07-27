#!/usr/bin/env python3
"""
GitHub MCP Agent Server for Claude Desktop
This file implements an MCP server that exposes the agent's capabilities to Claude Desktop.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Union
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from pydantic import AnyUrl

# Import our agent components
from dotenv import load_dotenv
from agent_demo import load_llm_config, create_llm, add_numbers, multiply_numbers, get_help

# Load environment variables
load_dotenv()

# Create the MCP server
server = Server("github-mcp-agent")

class AgentMCPServer:
    """MCP Server wrapper for our GitHub Agent"""
    
    def __init__(self):
        self.config = load_llm_config()
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM with fallback"""
        try:
            self.llm = create_llm(self.config)
            print(f"🤖 MCP Server: LLM initialized ({self.config.provider})", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ MCP Server: LLM failed to initialize: {e}", file=sys.stderr)
            self.llm = None

# Create server instance
agent_server = AgentMCPServer()

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for Claude Desktop"""
    return [
        types.Tool(
            name="add_numbers",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "First number to add"
                    },
                    "b": {
                        "type": "integer", 
                        "description": "Second number to add"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        types.Tool(
            name="multiply_numbers",
            description="Multiply two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "First number to multiply"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Second number to multiply" 
                    }
                },
                "required": ["x", "y"]
            }
        ),
        types.Tool(
            name="get_agent_help",
            description="Get information about the agent's capabilities",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_system_info",
            description="Get information about the MCP server and agent system",
            inputSchema={
                "type": "object", 
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls from Claude Desktop"""
    
    try:
        if name == "add_numbers":
            a = arguments.get("a")
            b = arguments.get("b")
            if a is None or b is None:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: Both 'a' and 'b' parameters are required for addition"
                )]
            
            result = add_numbers.invoke({"a": a, "b": b})
            return [types.TextContent(
                type="text", 
                text=f"🔢 Addition Result: {a} + {b} = {result}"
            )]
            
        elif name == "multiply_numbers":
            x = arguments.get("x")
            y = arguments.get("y")
            if x is None or y is None:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: Both 'x' and 'y' parameters are required for multiplication"
                )]
            
            result = multiply_numbers.invoke({"x": x, "y": y})
            return [types.TextContent(
                type="text",
                text=f"✖️ Multiplication Result: {x} × {y} = {result}"
            )]
            
        elif name == "get_agent_help":
            help_info = get_help.invoke({})
            return [types.TextContent(
                type="text",
                text=f"🤖 Agent Capabilities:\n{help_info}"
            )]
            
        elif name == "get_system_info":
            system_info = f"""
🏗️ GitHub MCP Agent System Information:

📋 Configuration:
- LLM Provider: {agent_server.config.provider}
- Ollama Model: {agent_server.config.ollama_model}
- Gemini Model: {agent_server.config.gemini_model}
- LLM Status: {'✅ Connected' if agent_server.llm else '❌ Not Connected'}

🔧 Available Tools:
- Mathematical operations (add, multiply)
- System information and help
- Future: GitHub repository management

🌐 MCP Integration:
- Server Status: Active
- Protocol: Model Context Protocol
- Client: Claude Desktop
            """
            return [types.TextContent(
                type="text",
                text=system_info.strip()
            )]
            
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ Error: Unknown tool '{name}'"
            )]
            
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error executing tool '{name}': {str(e)}"
        )]

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources"""
    return [
        types.Resource(
            uri=AnyUrl("agent://config"),
            name="Agent Configuration",
            description="Current agent configuration and status",
            mimeType="application/json"
        ),
        types.Resource(
            uri=AnyUrl("agent://capabilities"),
            name="Agent Capabilities", 
            description="Detailed information about agent capabilities",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Handle resource reading"""
    
    if str(uri) == "agent://config":
        config_data = {
            "provider": agent_server.config.provider,
            "ollama_model": agent_server.config.ollama_model,
            "gemini_model": agent_server.config.gemini_model,
            "llm_connected": agent_server.llm is not None,
            "tools_available": ["add_numbers", "multiply_numbers", "get_agent_help", "get_system_info"]
        }
        return json.dumps(config_data, indent=2)
        
    elif str(uri) == "agent://capabilities":
        return """
GitHub MCP Agent Capabilities:

🔧 Mathematical Operations:
- Addition of two integers
- Multiplication of two integers

🤖 System Operations:
- Configuration information
- Help and documentation
- Status monitoring

🔮 Future Capabilities:
- GitHub repository management
- Issue tracking and creation
- Pull request operations
- Code analysis and review

🌐 MCP Integration:
- Full Model Context Protocol support
- Claude Desktop integration
- Tool execution and resource access
- Real-time agent communication
        """.strip()
        
    else:
        raise ValueError(f"Unknown resource: {uri}")

async def main():
    """Main entry point for the MCP server"""
    # Provide server info
    print("🚀 Starting GitHub MCP Agent Server for Claude Desktop...", file=sys.stderr)
    print(f"📋 LLM Provider: {agent_server.config.provider}", file=sys.stderr)
    print("🔌 Server ready for Claude Desktop connection", file=sys.stderr)
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="github-mcp-agent",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
