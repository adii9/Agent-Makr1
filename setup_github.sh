#!/bin/bash
# GitHub Repository Setup Instructions
# Run this after creating a repository on GitHub.com

echo "🚀 GitHub Repository Setup Instructions"
echo "========================================"
echo ""
echo "1. 🌐 Go to https://github.com/new"
echo "2. 📝 Repository name: github-mcp-agent"
echo "3. 📖 Description: Autonomous agent using LangGraph and LangChain with GitHub MCP integration"
echo "4. 🔒 Choose Public or Private (recommended: Public for open source)"
echo "5. ❌ Do NOT initialize with README, .gitignore, or license (we already have them)"
echo "6. ✅ Click 'Create repository'"
echo ""
echo "7. 📋 After creating, copy the repository URL and run:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/github-mcp-agent.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🎉 Your code will then be available on GitHub!"
echo ""
echo "Alternative: If you have GitHub CLI installed, run:"
echo "   gh repo create github-mcp-agent --public --source=. --remote=origin --push"
