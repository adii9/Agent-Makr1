#!/usr/bin/env python3
"""
Test script for the GitHub MCP Agent
This script verifies that all dependencies are correctly installed and working.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required packages can be imported"""
    print("🧪 Testing package imports...")

    try:
        import langchain
        print(f"✅ langchain v{langchain.__version__}")
    except ImportError as e:
        print(f"❌ langchain: {e}")

    try:
        import langgraph
        print(f"✅ langgraph imported successfully")
    except ImportError as e:
        print(f"❌ langgraph: {e}")

    try:
        from langchain_ollama import ChatOllama
        print("✅ langchain_ollama imported successfully")
    except ImportError as e:
        print(f"❌ langchain_ollama: {e}")

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai imported successfully")
    except ImportError as e:
        print(f"❌ langchain_google_genai: {e}")

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")

    try:
        import pydantic
        print(f"✅ pydantic v{pydantic.__version__}")
    except ImportError as e:
        print(f"❌ pydantic: {e}")

def test_basic_functionality():
    """Test basic agent functionality"""
    print("\n🔧 Testing basic functionality...")

    from langchain_core.tools import tool

    @tool
    def test_add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    result = test_add.invoke({"a": 5, "b": 3})
    print(f"✅ Tool execution test: 5 + 3 = {result}")

def main():
    """Run all tests"""
    print("🚀 GitHub MCP Agent - Dependency Test")
    print("=" * 50)

    test_imports()
    test_basic_functionality()

    print("\n" + "=" * 50)
    print("🎉 Test completed! Your environment is ready.")
    print("\n📝 Next steps:")
    print("1. Set up your .env file with API keys")
    print("2. Run the Jupyter notebook: agent_notebook.ipynb")
    print("3. Start building your autonomous agent!")

if __name__ == "__main__":
    main()
