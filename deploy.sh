#!/bin/bash

# Flash USDT Bot - Railway Deployment Script

echo "⚡ Flash USDT Bot - Railway Deployment"
echo "========================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📥 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo ""
echo "🔧 Setting up environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  Edit .env with your credentials:"
    echo "   - TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo "   - ADMIN_ID (your Telegram user ID)"
    echo ""
    read -p "Press enter after updating .env..."
fi

echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo "🔗 Check your Railway dashboard: https://railway.app"
echo ""
echo "Test bot:"
echo "  1. Open Telegram"
echo "  2. Find your bot (@your_bot_name)"
echo "  3. Send /start"
