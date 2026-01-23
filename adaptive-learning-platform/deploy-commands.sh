#!/bin/bash

echo "🚀 Render Deployment - Quick Start"
echo "===================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Adaptive Learning Platform"
    git branch -M main
    echo "✅ Git initialized"
    echo ""
    echo "⚠️  Next: Add your GitHub remote:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/adaptive-learning-platform.git"
    echo "   git push -u origin main"
else
    echo "✅ Git already initialized"
    echo ""
    echo "📤 Committing and pushing changes..."
    git add .
    git commit -m "Fixed Render deployment configuration"
    git push origin main
    echo "✅ Changes pushed to GitHub"
fi

echo ""
echo "======================================"
echo "🎯 Next Steps:"
echo "======================================"
echo ""
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Render will detect render.yaml automatically ✅"
echo ""
echo "5. Add these Environment Variables:"
echo "   MONGODB_URI = mongodb+srv://kartikarora3135:Ak31351240.!@csa.spxmhnr.mongodb.net/?appName=CSA"
echo "   SECRET_KEY = af8d9c6e4b3a2f1d8e7c6b5a4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a"
echo "   OPENROUTER_API_KEY = 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"
echo "   LLM_PROVIDER = openrouter"
echo "   OPENROUTER_MODEL = mistralai/mistral-7b-instruct"
echo ""
echo "6. Click 'Create Web Service'"
echo ""
echo "7. Wait 3-5 minutes for deployment"
echo ""
echo "8. Test your API:"
echo "   curl https://your-app.onrender.com/health"
echo ""
echo "✅ Deployment Ready!"
echo ""
echo "📚 Full Guide: RENDER_DEPLOYMENT.md"
