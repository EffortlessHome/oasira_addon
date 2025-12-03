#!/bin/bash

# Build script for Oasira addon

set -e

echo "📦 Copying dashboard dist folder..."
if [ -d "../oasira-dashboard/dist" ]; then
    cp -r ../oasira-dashboard/dist oasira_cloud_bridge/dist
    echo "✅ Dashboard dist copied successfully"
else
    echo "⚠️ WARNING: Dashboard dist folder not found at ../oasira-dashboard/dist"
    echo "   Build will continue but dashboard may not be available"
fi

echo ""
echo "🔨 Building Oasira Addon..."
cd oasira_cloud_bridge

# Build the addon
docker build -t oasira-addon:latest .

cd ..
echo ""
echo "✅ Build complete!"
echo "To test locally, run: docker run -p 8080:8080 oasira-addon:latest"
