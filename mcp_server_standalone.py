#!/usr/bin/env python3
"""
Standalone GitHub MCP Agent Server for Claude Desktop
This version includes all dependencies inline for maximum compatibility.
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Check if we're running in the virtual environment
venv_python = current_dir / ".venv" / "bin" / "python"
if venv_python.exists() and sys.executable != str(venv_python):
    print(f"🔄 Switching to virtual environment Python...", file=sys.stderr)
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
    from pydantic import AnyUrl
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}", file=sys.stderr)
    print(f"💡 Please ensure all dependencies are installed:", file=sys.stderr)
    print(f"   cd {current_dir}", file=sys.stderr)
    print(f"   uv sync", file=sys.stderr)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Create the MCP server
server = Server("github-mcp-agent")

# Simple mock LLM for demo purposes
class MockLLMConfig:
    def __init__(self):
        self.provider = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")

class AgentMCPServer:
    """MCP Server wrapper for our GitHub Agent"""

    def __init__(self):
        self.config = MockLLMConfig()
        print(f"🤖 MCP Server initialized with provider: {self.config.provider}", file=sys.stderr)

# Create server instance
agent_server = AgentMCPServer()

# Tool implementations
def add_numbers_impl(a: int, b: int) -> int:
    """Add two numbers together"""
    result = a + b
    print(f"🔢 Adding {a} + {b} = {result}", file=sys.stderr)
    return result

def multiply_numbers_impl(x: int, y: int) -> int:
    """Multiply two numbers together"""
    result = x * y
    print(f"✖️ Multiplying {x} × {y} = {result}", file=sys.stderr)
    return result

def get_help_impl() -> str:
    """Get agent help information"""
    return """
🤖 I'm an autonomous agent with the following capabilities:

📊 Mathematical Operations:
- Add two numbers: "add 5 and 3"
- Multiply two numbers: "multiply 4 by 6"

🔮 Future Capabilities (coming soon):
- GitHub repository management
- Issue tracking and creation
- Pull request operations

Just ask me to perform any of these operations!
    """.strip()

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

    print(f"🔧 Tool called: {name} with args: {arguments}", file=sys.stderr)

    try:
        if name == "add_numbers":
            a = arguments.get("a")
            b = arguments.get("b")
            if a is None or b is None:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: Both 'a' and 'b' parameters are required for addition"
                )]

            result = add_numbers_impl(a, b)
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

            result = multiply_numbers_impl(x, y)
            return [types.TextContent(
                type="text",
                text=f"✖️ Multiplication Result: {x} × {y} = {result}"
            )]

        elif name == "get_agent_help":
            help_info = get_help_impl()
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
- Python Version: {sys.version.split()[0]}
- Working Directory: {Path.cwd()}

🔧 Available Tools:
- Mathematical operations (add, multiply)
- System information and help
- Future: GitHub repository management

🌐 MCP Integration:
- Server Status: Active ✅
- Protocol: Model Context Protocol
- Client: Claude Desktop
- Connection: Established
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
        error_msg = f"❌ Error executing tool '{name}': {str(e)}"
        print(error_msg, file=sys.stderr)
        return [types.TextContent(
            type="text",
            text=error_msg
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
            "python_version": sys.version.split()[0],
            "working_directory": str(Path.cwd()),
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
    print("🚀 Starting GitHub MCP Agent Server for Claude Desktop...", file=sys.stderr)
    print(f"📋 LLM Provider: {agent_server.config.provider}", file=sys.stderr)
    print(f"🐍 Python: {sys.executable}", file=sys.stderr)
    print(f"📁 Working Directory: {Path.cwd()}", file=sys.stderr)
    print("🔌 Server ready for Claude Desktop connection", file=sys.stderr)

    try:
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
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    asyncio.run(main())
