# GitHub MCP Agent 🤖

An autonomous agent built with LangGraph and LangChain that integrates with GitHub using Model Context Protocol (MCP). The agent supports configurable LLM backends (Ollama and Gemini) and can perform mathematical operations and GitHub repository management.

## Features ✨

- **🔧 Configurable LLM Backends**: Switch between Ollama (local) and Gemini (cloud) easily
- **📊 Mathematical Operations**: Add and multiply numbers with tool integration
- **🐙 GitHub Integration**: Repository information and issue management (via MCP)
- **🔄 Autonomous Workflow**: LangGraph-powered conversation flow
- **💾 Memory Management**: Persistent conversation state
- **🛠️ Extensible Architecture**: Easy to add new tools and capabilities

## Quick Start 🚀

### Prerequisites

- Python 3.13+
- [UV](https://docs.astral.sh/uv/) package manager
- [Ollama](https://ollama.ai) (optional, for local LLM)
- Google API key (optional, for Gemini)
- GitHub token (optional, for GitHub integration)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/adii9/Agent-Makr1.git
   cd Agent-Makr1
   ```

2. **Install dependencies with UV**:
   ```bash
   uv sync
   ```

3. **Configure environment** (copy and edit):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

### Usage

#### Option 1: Python Script (Recommended for testing)
```bash
uv run python agent_demo.py
```

#### Option 2: Jupyter Notebook (For development)
```bash
uv run jupyter lab agent_notebook.ipynb
```

#### Option 3: Test Setup
```bash
uv run python test_setup.py
```

#### Option 4: Claude Desktop Integration (MCP)
```bash
# Set up Claude Desktop integration
uv run python setup_claude.py

# Restart Claude Desktop, then use commands like:
# "Add 15 and 27" or "Get system information"
```

## Configuration ⚙️

### Environment Variables

Create a `.env` file with your configuration:

```env
# LLM Provider Configuration
DEFAULT_LLM_PROVIDER=ollama  # or "gemini"

# Ollama Configuration (for local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Gemini Configuration (for cloud LLM)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-pro

# GitHub Configuration (for MCP integration)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_username/your_repo
```

### Setting up Ollama (Local LLM)

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama2
   # or try: ollama pull llama3, ollama pull codellama, etc.
   ```
3. Start Ollama service (usually runs automatically)

### Setting up Gemini (Cloud LLM)

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file
3. Set `DEFAULT_LLM_PROVIDER=gemini`

## Claude Desktop Integration 🤖

This agent can be integrated with Claude Desktop as an MCP (Model Context Protocol) server, allowing Claude to use the agent's tools directly.

### Setup Claude Desktop Integration

1. **Run the setup script**:
   ```bash
   uv run python setup_claude.py
   ```

2. **Restart Claude Desktop** application

3. **Test the integration** with natural language:
   ```
   "Add 15 and 27"
   "Multiply 8 by 9"
   "Get system information"
   "What mathematical operations can you perform?"
   ```

### Available MCP Tools

When connected to Claude Desktop, the following tools are available:
- `add_numbers` - Add two integers
- `multiply_numbers` - Multiply two integers
- `get_agent_help` - Show agent capabilities
- `get_system_info` - Display system and configuration info

### Troubleshooting Claude Desktop

- Ensure Claude Desktop is completely restarted after setup
- Check that UV and Python are in your system PATH
- Verify configuration with: `uv run python setup_claude.py --test`
- View Claude Desktop logs if tools don't appear

## Project Structure 📁

```
github-mcp-agent/
├── agent_demo.py              # Main Python demo script
├── agent_notebook.ipynb       # Jupyter notebook with full tutorial
├── test_setup.py              # Dependency and setup verification
├── mcp_server.py              # MCP server for Claude Desktop integration
├── setup_claude.py            # Claude Desktop setup script
├── claude_desktop_config.json # Example Claude Desktop configuration
├── pyproject.toml             # Project configuration and dependencies
├── .env.example               # Environment variables template
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT license
└── README.md                 # This file
```

## Architecture 🏗️

The agent is built using:

- **LangGraph**: State machine for conversation flow
- **LangChain**: LLM integration and tool management
- **Pydantic**: Configuration and data validation
- **UV**: Fast Python package management

### Agent Workflow

1. **User Input** → Assistant (LLM processes request)
2. **Decision Point** → Use tools or respond directly
3. **Tool Execution** → If needed, execute mathematical or GitHub operations
4. **Response** → Return results to user

## Available Tools 🛠️

### Mathematical Operations
- `add_numbers(a, b)` - Add two integers
- `multiply_numbers(x, y)` - Multiply two integers
- `get_help()` - Show available capabilities

### GitHub Operations (Future)
- `get_repo_info(repo_name)` - Get repository information
- `list_repo_issues(repo_name)` - List repository issues

## Development 👩‍💻

### Adding New Tools

```python
from langchain_core.tools import tool

@tool
def your_custom_tool(param: str) -> str:
    """Description of your tool"""
    # Your implementation here
    return result

# Add to tools list in agent creation
tools = [add_numbers, multiply_numbers, your_custom_tool]
```

### Extending LLM Support

1. Add new LLM configuration in `LLMConfig`
2. Update `create_llm()` function
3. Add provider-specific initialization

## Examples 💡

### Basic Mathematical Operations
```python
# Through the agent interface
"Add 15 and 27"           # → Uses add_numbers tool
"Multiply 8 by 9"         # → Uses multiply_numbers tool
"What can you help with?" # → Shows capabilities
```

### GitHub Operations (Future)
```python
"Get info about microsoft/vscode"    # → Repository details
"List issues from python/cpython"    # → Recent issues
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting 🔍

### Common Issues

1. **Ollama Connection Failed**:
   - Ensure Ollama is installed and running
   - Check if the model is pulled: `ollama list`
   - Verify the base URL in `.env`

2. **Gemini API Errors**:
   - Verify your API key is correct
   - Check API quotas and limits
   - Ensure you have access to the specified model

3. **Import Errors**:
   - Run `uv sync` to install dependencies
   - Ensure you're using the project's virtual environment

### Getting Help

- Check the Jupyter notebook for detailed explanations
- Run `test_setup.py` to verify your environment
- Review the `.env.example` for configuration examples

---

**Built with ❤️ using LangGraph, LangChain, and UV**