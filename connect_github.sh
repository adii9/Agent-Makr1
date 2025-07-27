#!/bin/bash
# Quick setup script for connecting to GitHub remote repository
# Usage: ./connect_github.sh <your-github-username>

if [ -z "$1" ]; then
    echo "❌ Usage: ./connect_github.sh <your-github-username>"
    echo "📝 Example: ./connect_github.sh adiimathur"
    exit 1
fi

USERNAME=$1
REPO_NAME="github-mcp-agent"
GITHUB_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "🔗 Setting up GitHub remote repository..."
echo "📍 Repository URL: ${GITHUB_URL}"
echo ""

# Add the remote origin
echo "🔧 Adding remote origin..."
git remote add origin "${GITHUB_URL}"

# Ensure we're on the main branch
echo "🌿 Setting up main branch..."
git branch -M main

# Push to GitHub
echo "📤 Pushing code to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "🌐 Your repository is now available at: https://github.com/${USERNAME}/${REPO_NAME}"
echo ""
echo "🎯 Next steps:"
echo "   1. Visit your repository on GitHub"
echo "   2. Add any additional repository settings (description, topics, etc.)"
echo "   3. Consider adding a LICENSE file"
echo "   4. Set up branch protection rules if needed"
