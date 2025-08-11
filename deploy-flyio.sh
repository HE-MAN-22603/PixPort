#!/bin/bash

# ========================================
# 🚀 PixPort Fly.io Deployment Script
# ========================================
# Deploys PixPort with isnet-general-use model to Fly.io FREE PLAN
# Run this script to deploy your app automatically

echo "🪂 PixPort Fly.io Deployment Script"
echo "===================================="
echo "📦 Model: isnet-general-use (40MB)"
echo "💾 Plan: FREE (256MB memory)"
echo "🌍 Region: Mumbai (bom)"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed!"
    echo "📥 Install it from: https://fly.io/docs/flyctl/install/"
    echo "💡 On Windows: winget install fly-io.flyctl"
    echo "💡 On Mac: brew install flyctl"
    exit 1
fi

echo "✅ flyctl found: $(flyctl version)"

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Not logged in to Fly.io"
    echo "👤 Logging in..."
    flyctl auth login
fi

echo "✅ Logged in as: $(flyctl auth whoami)"

# Check if app exists
APP_NAME="pixport-bg-remover"
echo "🔍 Checking if app '$APP_NAME' exists..."

if flyctl apps list | grep -q "$APP_NAME"; then
    echo "✅ App exists, deploying update..."
    flyctl deploy --dockerfile Dockerfile.flyio
else
    echo "📱 App doesn't exist, creating new app..."
    echo "🚀 Launching new Fly.io app..."
    
    # Create app with specific configuration
    flyctl apps create "$APP_NAME" --org personal
    
    echo "🔧 Deploying application..."
    flyctl deploy --dockerfile Dockerfile.flyio
fi

echo ""
echo "🎉 Deployment Complete!"
echo "========================"
echo "🌐 Your app URL: https://$APP_NAME.fly.dev"
echo "🏥 Health check: https://$APP_NAME.fly.dev/health"
echo "📊 Status: https://$APP_NAME.fly.dev/flyio-status"
echo "💾 Memory: https://$APP_NAME.fly.dev/memory"
echo ""
echo "🔧 Useful commands:"
echo "   flyctl status                    # Check app status"
echo "   flyctl logs                      # View logs"
echo "   flyctl ssh console              # SSH into app"
echo "   flyctl scale show               # View scaling"
echo "   flyctl dashboard                # Open dashboard"
echo ""
echo "💡 FREE PLAN NOTES:"
echo "   • 256MB memory (tight but workable)"
echo "   • Auto-sleep when not in use"
echo "   • First request may be slow (cold start)"
echo "   • Consider upgrading to $5/month plan for 512MB"
echo ""
echo "🎯 Model Info:"
echo "   • Using: isnet-general-use"
echo "   • Size: 40MB"
echo "   • Accuracy: 90%+"
echo "   • Speed: 2-3 seconds"
echo ""
echo "✅ Ready to process images! 🖼️"
