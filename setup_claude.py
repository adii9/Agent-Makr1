#!/usr/bin/env python3
"""
Claude Desktop Setup Script for GitHub MCP Agent
This script helps configure Claude Desktop to use our MCP server.
"""

import json
import os
import shutil
from pathlib import Path
import sys

def get_claude_config_path():
    """Get the Claude Desktop configuration file path based on OS"""
    home = Path.home()

    if sys.platform == "darwin":  # macOS
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return home / ".config" / "claude" / "claude_desktop_config.json"

def backup_existing_config(config_path):
    """Backup existing Claude Desktop configuration"""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backed up existing config to: {backup_path}")
        return True
    return False

def load_existing_config(config_path):
    """Load existing Claude Desktop configuration"""
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Existing config file has invalid JSON, creating new one")
            return {}
    return {}

def setup_claude_desktop():
    """Main setup function"""
    print("🚀 Claude Desktop Setup for GitHub MCP Agent")
    print("=" * 50)

    # Get paths
    project_root = Path(__file__).parent.absolute()
    mcp_server_path = project_root / "mcp_server.py"
    config_path = get_claude_config_path()

    print(f"📁 Project root: {project_root}")
    print(f"🔧 MCP server: {mcp_server_path}")
    print(f"⚙️ Claude config: {config_path}")

    # Verify MCP server exists
    if not mcp_server_path.exists():
        print(f"❌ Error: MCP server file not found at {mcp_server_path}")
        return False

    # Find UV path
    uv_path = shutil.which("uv")
    if not uv_path:
        # Try common locations
        common_uv_paths = [
            Path.home() / ".local" / "bin" / "uv",
            Path("/usr/local/bin/uv"),
            Path("/opt/homebrew/bin/uv")
        ]
        for path in common_uv_paths:
            if path.exists():
                uv_path = str(path)
                break

    # Find Python path in the virtual environment
    venv_python = project_root / ".venv" / "bin" / "python"

    print(f"🔍 UV path: {uv_path}")
    print(f"🐍 Python venv: {venv_python}")

    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing config
    backup_existing_config(config_path)

    # Load existing config
    config = load_existing_config(config_path)

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Choose the best configuration method - use bash wrapper for maximum compatibility
    wrapper_script_path = project_root / "run_mcp_server.sh"
    standalone_server_path = project_root / "mcp_server_standalone.py"

    if wrapper_script_path.exists():
        print("✅ Using bash wrapper script (handles spaces in paths)")
        # Use the bash wrapper script that handles all the complexity
        config["mcpServers"]["github-mcp-agent"] = {
            "command": str(wrapper_script_path),
            "args": []
        }
    elif standalone_server_path.exists():
        print("✅ Using standalone MCP server")
        # Use the standalone server that handles its own dependencies
        config["mcpServers"]["github-mcp-agent"] = {
            "command": str(venv_python) if venv_python.exists() else (shutil.which("python3") or shutil.which("python")),
            "args": [
                str(standalone_server_path)
            ],
            "env": {
                "PYTHONPATH": f'"{project_root}"'  # Quote the path to handle spaces
            }
        }
    elif uv_path and Path(uv_path).exists():
        print("✅ Using UV with full path")
        # Add our MCP server configuration with full UV path
        config["mcpServers"]["github-mcp-agent"] = {
            "command": uv_path,
            "args": [
                "run",
                "--directory", f'"{project_root}"',  # Quote directory path
                "python",
                str(mcp_server_path)
            ],
            "env": {
                "PYTHONPATH": f'"{project_root}"'  # Quote the path to handle spaces
            }
        }
    elif venv_python.exists():
        print("✅ Using virtual environment Python directly")
        # Use the virtual environment Python directly
        config["mcpServers"]["github-mcp-agent"] = {
            "command": str(venv_python),
            "args": [
                str(mcp_server_path)
            ],
            "env": {
                "PYTHONPATH": f'"{project_root}"'  # Quote the path to handle spaces
            }
        }
    else:
        print("⚠️ Using system Python (less reliable)")
        # Fallback to system Python
        python_path = shutil.which("python3") or shutil.which("python")
        config["mcpServers"]["github-mcp-agent"] = {
            "command": python_path,
            "args": [
                str(mcp_server_path)
            ],
            "env": {
                "PYTHONPATH": f'"{project_root}"'  # Quote the path to handle spaces
            }
        }

    # Write the updated configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Successfully updated Claude Desktop configuration!")
        print(f"📝 Configuration saved to: {config_path}")

        print("\n🎯 Next Steps:")
        print("1. 🔄 Restart Claude Desktop application")
        print("2. 🔌 The GitHub MCP Agent should now be available in Claude")
        print("3. 🧪 Test with commands like: 'Add 15 and 27' or 'Get system info'")
        print("4. 🛠️ Use tools: add_numbers, multiply_numbers, get_agent_help")

        return True

    except Exception as e:
        print(f"❌ Error writing configuration: {e}")
        return False

def test_mcp_server():
    """Test the MCP server configuration"""
    print("\n🧪 Testing MCP Server Configuration...")
    print("=" * 50)

    project_root = Path(__file__).parent.absolute()

    # Test if we can import required modules
    sys.path.insert(0, str(project_root))

    try:
        import mcp
        print("✅ MCP library available")
    except ImportError:
        print("❌ MCP library not found - ensure dependencies are installed")
        return False

    try:
        from agent_demo import load_llm_config
        config = load_llm_config()
        print(f"✅ Agent configuration loaded: {config.provider}")
    except Exception as e:
        print(f"❌ Error loading agent config: {e}")
        return False

    print("✅ MCP server configuration test passed!")
    return True

def show_usage_examples():
    """Show example commands for Claude Desktop"""
    print("\n📚 Usage Examples for Claude Desktop:")
    print("=" * 50)

    examples = [
        {
            "description": "Basic Mathematics",
            "commands": [
                "Add 25 and 17",
                "Multiply 8 by 9",
                "What's 100 plus 200?"
            ]
        },
        {
            "description": "Agent Information",
            "commands": [
                "Get agent help",
                "Show system information",
                "What can you help me with?"
            ]
        },
        {
            "description": "MCP Tools (Direct)",
            "commands": [
                "Use add_numbers tool with a=15, b=27",
                "Use multiply_numbers tool with x=6, y=7",
                "Use get_system_info tool"
            ]
        }
    ]

    for example in examples:
        print(f"\n🔹 {example['description']}:")
        for cmd in example['commands']:
            print(f"   💬 \"{cmd}\"")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mcp_server()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_usage_examples()
        return

    # Run setup
    success = setup_claude_desktop()

    if success:
        show_usage_examples()

        print(f"\n🔍 Troubleshooting:")
        print("- If Claude Desktop doesn't see the agent, check the logs")
        print("- Ensure UV and Python are in your PATH")
        print("- Run with --test flag to verify configuration")
        print("- Check that dependencies are installed: uv sync")

    print(f"\n📖 For more information, see the README.md file")

if __name__ == "__main__":
    main()
