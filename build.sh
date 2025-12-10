#!/bin/bash

# Build script for Oasira addon

set -e

echo "📦 Copying dashboard dist folder..."
if [ -d "../oasira-dashboard/dist" ]; then
    # Clean old dist folder first
    rm -rf oasira_cloud_bridge/dist
    cp -r ../oasira-dashboard/dist oasira_cloud_bridge/dist
    echo "✅ Dashboard dist copied successfully"
else
    echo "⚠️ WARNING: Dashboard dist folder not found at ../oasira-dashboard/dist"
    echo "   Build will continue but dashboard may not be available"
fi

echo ""
echo "🔨 Building Oasira Addon with optimizations..."
cd oasira_cloud_bridge

# Build the addon with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --progress=plain \
    -t oasira-addon:latest .

cd ..
echo ""
echo "✅ Build complete!"
echo "To test locally, run: docker run -p 8080:8080 oasira-addon:latest"
