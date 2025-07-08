#!/bin/bash

# Setup script for Renovate GitHub Action secrets
# This script helps you create and configure the required secrets for Renovate

set -e

echo "🔧 Setting up Renovate GitHub Action secrets..."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   brew install gh"
    echo "   or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI. Please run:"
    echo "   gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"
echo ""

# Instructions for creating PAT token
echo "🔑 STEP 1: Create a Personal Access Token (PAT)"
echo ""
echo "You need to create a Personal Access Token with the following permissions:"
echo "  - repo (Full control of private repositories)"
echo "  - workflow (Update GitHub Action workflows)"
echo ""
echo "To create the token:"
echo "  1. Go to: https://github.com/settings/tokens"
echo "  2. Click 'Generate new token (classic)'"
echo "  3. Set expiration (recommend 90 days or 1 year)"
echo "  4. Select scopes: 'repo' and 'workflow'"
echo "  5. Click 'Generate token'"
echo "  6. Copy the token (you won't see it again!)"
echo ""

# Prompt for PAT token
echo "🔐 STEP 2: Set up the RENOVATE_TOKEN secret"
echo ""
read -s -p "Paste your Personal Access Token here: " PAT_TOKEN
echo ""

if [ -z "$PAT_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Set the secret
echo "📝 Setting RENOVATE_TOKEN secret..."
echo "$PAT_TOKEN" | gh secret set RENOVATE_TOKEN --repo "$REPO"

if [ $? -eq 0 ]; then
    echo "✅ RENOVATE_TOKEN secret set successfully!"
else
    echo "❌ Failed to set RENOVATE_TOKEN secret"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Commit and push the workflow files:"
echo "   git add .github/"
echo "   git commit -m 'feat: add renovate github action workflow'"
echo "   git push"
echo ""
echo "2. Test the workflow:"
echo "   - Go to: https://github.com/$REPO/actions"
echo "   - Find the 'Renovate' workflow"
echo "   - Click 'Run workflow' to test manually"
echo ""
echo "3. The workflow will run automatically every Monday at 9:00 AM UTC"
echo ""
echo "📚 Configuration files created:"
echo "  - .github/workflows/renovate.yml"
echo "  - .github/renovate.json"
echo ""
echo "For more configuration options, see:"
echo "  https://docs.renovatebot.com/configuration-options/"
