#!/bin/bash

echo "🐙 Meta Ad Creatives AI - GitHub Setup"
echo "======================================"
echo ""

# Check if repository already has a remote
if git remote -v | grep -q origin; then
    echo "✅ Remote origin already configured:"
    git remote -v
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push -u origin main
else
    echo "Please provide your GitHub username:"
    read -p "GitHub username: " username
    
    if [ -z "$username" ]; then
        echo "❌ Username is required!"
        exit 1
    fi
    
    echo ""
    echo "🔗 Adding GitHub remote..."
    git remote add origin "https://github.com/$username/meta-ad-creatives-ai.git"
    
    echo "📤 Pushing to GitHub..."
    git branch -M main
    git push -u origin main
fi

echo ""
echo "✅ Success! Your Meta Ad Creatives AI project is now on GitHub!"
echo "🌐 Repository URL: https://github.com/$username/meta-ad-creatives-ai"
echo ""
echo "📋 Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add your Gemini API key to .env file locally"
echo "3. Run: ./run.sh to start the application"
echo "4. Share with your team! 🎉"
