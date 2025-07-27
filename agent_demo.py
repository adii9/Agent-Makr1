#!/usr/bin/env python3
"""
GitHub MCP Agent - Simple Python Version
A demonstration of an autonomous agent using LangGraph and LangChain.
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal, Optional, Annotated, Sequence, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """Configuration for LLM connections"""
    provider: Literal["ollama", "gemini"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"

def load_llm_config() -> LLMConfig:
    """Load LLM configuration from environment variables"""
    return LLMConfig(
        provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama2"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-pro")
    )

def create_llm(config: LLMConfig):
    """Create LLM instance based on configuration"""
    if config.provider == "ollama":
        print(f"🦙 Initializing Ollama with model: {config.ollama_model}")
        return ChatOllama(
            base_url=config.ollama_base_url,
            model=config.ollama_model,
            temperature=0.1
        )
    elif config.provider == "gemini":
        if not config.google_api_key:
            raise ValueError("Google API key is required for Gemini provider")
        print(f"🤖 Initializing Gemini with model: {config.gemini_model}")
        return ChatGoogleGenerativeAI(
            model=config.gemini_model,
            google_api_key=config.google_api_key,
            temperature=0.1
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")

# Define tools
@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    result = a + b
    print(f"🔢 Adding {a} + {b} = {result}")
    return result

@tool
def multiply_numbers(x: int, y: int) -> int:
    """Multiply two numbers together."""
    result = x * y
    print(f"✖️ Multiplying {x} × {y} = {result}")
    return result

@tool
def get_help() -> str:
    """Get information about available capabilities."""
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
    """

# Agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def create_agent():
    """Create and return the agent"""
    # Load configuration
    config = load_llm_config()
    print(f"📋 Configured for LLM provider: {config.provider}")

    # Define tools first
    tools = [add_numbers, multiply_numbers, get_help]

    # Create LLM (with fallback for demo)
    try:
        llm = create_llm(config)
        print("✅ LLM connected successfully!")
        llm_with_tools = llm.bind_tools(tools)
    except Exception as e:
        print(f"⚠️ LLM connection failed: {e}")
        print("🔄 Using demo mode with simulated responses")

        class MockLLM:
            def invoke(self, messages):
                last_message = messages[-1].content.lower() if messages else ""

                # Simple pattern matching for demo
                if "help" in last_message or "what" in last_message:
                    return AIMessage(content="I can help you with mathematical operations! Try asking me to add or multiply numbers.")
                elif "add" in last_message and any(char.isdigit() for char in last_message):
                    # Extract numbers for addition
                    import re
                    numbers = re.findall(r'\d+', last_message)
                    if len(numbers) >= 2:
                        return AIMessage(
                            content=f"I'll add {numbers[0]} and {numbers[1]} for you.",
                            tool_calls=[{
                                "name": "add_numbers",
                                "args": {"a": int(numbers[0]), "b": int(numbers[1])},
                                "id": "call_add"
                            }]
                        )
                elif "multiply" in last_message and any(char.isdigit() for char in last_message):
                    # Extract numbers for multiplication
                    import re
                    numbers = re.findall(r'\d+', last_message)
                    if len(numbers) >= 2:
                        return AIMessage(
                            content=f"I'll multiply {numbers[0]} by {numbers[1]} for you.",
                            tool_calls=[{
                                "name": "multiply_numbers",
                                "args": {"x": int(numbers[0]), "y": int(numbers[1])},
                                "id": "call_multiply"
                            }]
                        )

                return AIMessage(content="I can help you with adding and multiplying numbers. Try saying 'add 5 and 3' or 'multiply 4 by 6'!")

            def bind_tools(self, tools):
                return self

        llm_with_tools = MockLLM()

    # Define nodes
    def call_model(state: AgentState):
        """Call the LLM with current state"""
        print("🤖 Processing your request...")
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Create workflow
    workflow = StateGraph(AgentState)
    workflow.add_node("assistant", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("assistant")
    workflow.add_conditional_edges(
        "assistant",
        tools_condition,
        {"tools": "tools", "__end__": END}
    )
    workflow.add_edge("tools", "assistant")

    # Compile agent
    agent = workflow.compile(checkpointer=MemorySaver())
    print("✅ Agent created successfully!")
    return agent

def chat_with_agent(agent, query: str):
    """Chat with the agent"""
    print(f"\n👤 You: {query}")
    print("─" * 50)

    config = {"configurable": {"thread_id": "main-conversation"}}

    try:
        for chunk in agent.stream({"messages": [HumanMessage(content=query)]}, config=config):
            if "assistant" in chunk:
                message = chunk["assistant"]["messages"][0]
                if hasattr(message, 'content'):
                    print(f"🤖 Assistant: {message.content}")
            elif "tools" in chunk:
                for tool_call in chunk["tools"]["messages"]:
                    if hasattr(tool_call, 'content'):
                        print(f"🔧 Tool: {tool_call.content}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 GitHub MCP Agent - Python Version")
    print("=" * 50)

    # Create agent
    agent = create_agent()

    # Test queries
    test_queries = [
        "What can you help me with?",
        "Add 15 and 27",
        "Multiply 8 by 9",
        "Calculate 10 plus 5, then multiply by 2"
    ]

    print("\n🧪 Running test scenarios...")
    for query in test_queries:
        chat_with_agent(agent, query)
        print()

    # Interactive mode
    print("💬 Interactive mode (type 'quit' to exit):")
    print("─" * 50)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if user_input:
                chat_with_agent(agent, user_input)
        except KeyboardInterrupt:
            break

    print("\n👋 Goodbye! Thanks for using the GitHub MCP Agent!")

if __name__ == "__main__":
    main()
